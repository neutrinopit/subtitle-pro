"""
Flask Application - Subtitle Translator Pro
Professional subtitle translation application with AI support
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import json
import zipfile
from datetime import datetime
from typing import List, Dict, Any
import threading
import time

from config import Config
from utils.subtitle_parser import SubtitleParser, SubtitleEntry
from utils.translation_engine import TranslationEngine

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize translation engine
translation_engine = TranslationEngine(
    gemini_api_key=Config.GEMINI_API_KEY,
    deepl_api_key=Config.DEEPL_API_KEY
)

# Storage for translation jobs
translation_jobs = {}
translation_lock = threading.Lock()

# Create necessary directories
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def get_file_format(filename: str) -> str:
    """Get file format from filename"""
    return filename.rsplit('.', 1)[1].lower()


class TranslationJob:
    """Represents a translation job"""
    
    def __init__(self, job_id: str, files: List[Dict[str, Any]], 
                 source_lang: str, target_lang: str, service: str,
                 use_context: bool = False):
        self.job_id = job_id
        self.files = files
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.service = service
        self.use_context = use_context
        self.status = 'pending'
        self.progress = 0
        self.results = []
        self.error = None
        self.created_at = datetime.now()
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'job_id': self.job_id,
            'status': self.status,
            'progress': self.progress,
            'total_files': len(self.files),
            'source_lang': self.source_lang,
            'target_lang': self.target_lang,
            'service': self.service,
            'results': self.results,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


def process_translation_job(job: TranslationJob):
    """Process translation job in background"""
    try:
        job.status = 'processing'
        total_files = len(job.files)
        
        for idx, file_info in enumerate(job.files):
            try:
                # Read file
                file_path = file_info['path']
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Parse subtitles
                file_format = file_info['format']
                entries = SubtitleParser.parse(content, file_format)
                
                # Extract texts
                texts = [entry.text for entry in entries]
                
                # Translate
                translated_texts = translation_engine.batch_translate(
                    texts=texts,
                    source_lang=job.source_lang,
                    target_lang=job.target_lang,
                    service_name=job.service,
                    use_context=job.use_context,
                    context_window=Config.CONTEXT_WINDOW_SIZE
                )
                
                # Create translated entries
                translated_entries = []
                for entry, translated_text in zip(entries, translated_texts):
                    translated_entry = SubtitleEntry(
                        index=entry.index,
                        start_time=entry.start_time,
                        end_time=entry.end_time,
                        text=translated_text
                    )
                    translated_entries.append(translated_entry)
                
                # Format output
                output_content = SubtitleParser.format_output(translated_entries, file_format)
                
                # Save translated file
                output_filename = f"{file_info['name']}_translated.{file_format}"
                output_path = os.path.join(Config.OUTPUT_FOLDER, job.job_id, output_filename)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                
                # Add result
                job.results.append({
                    'original_name': file_info['name'],
                    'translated_name': output_filename,
                    'path': output_path,
                    'entries': len(translated_entries),
                    'status': 'completed'
                })
                
            except Exception as e:
                job.results.append({
                    'original_name': file_info['name'],
                    'error': str(e),
                    'status': 'failed'
                })
            
            # Update progress
            job.progress = int(((idx + 1) / total_files) * 100)
        
        job.status = 'completed'
        job.completed_at = datetime.now()
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.completed_at = datetime.now()


@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/services', methods=['GET'])
def get_services():
    """Get available translation services"""
    services = translation_engine.get_service_info()
    return jsonify({
        'success': True,
        'services': services
    })


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    languages = {
        'ar': 'Arabic (العربية)',
        'en': 'English',
        'es': 'Spanish (Español)',
        'fr': 'French (Français)',
        'de': 'German (Deutsch)',
        'it': 'Italian (Italiano)',
        'pt': 'Portuguese (Português)',
        'ru': 'Russian (Русский)',
        'zh': 'Chinese (中文)',
        'ja': 'Japanese (日本語)',
        'ko': 'Korean (한국어)',
        'tr': 'Turkish (Türkçe)',
        'hi': 'Hindi (हिन्दी)',
        'nl': 'Dutch (Nederlands)',
        'pl': 'Polish (Polski)',
        'sv': 'Swedish (Svenska)',
        'da': 'Danish (Dansk)',
        'fi': 'Finnish (Suomi)',
        'no': 'Norwegian (Norsk)',
        'cs': 'Czech (Čeština)',
        'el': 'Greek (Ελληνικά)',
        'he': 'Hebrew (עברית)',
        'th': 'Thai (ไทย)',
        'vi': 'Vietnamese (Tiếng Việt)',
        'id': 'Indonesian (Bahasa Indonesia)',
        'ms': 'Malay (Bahasa Melayu)',
        'uk': 'Ukrainian (Українська)',
        'ro': 'Romanian (Română)',
        'hu': 'Hungarian (Magyar)',
    }
    
    return jsonify({
        'success': True,
        'languages': languages
    })


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Upload subtitle files"""
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    
    if len(files) > Config.MAX_FILES_PER_BATCH:
        return jsonify({
            'success': False,
            'error': f'Maximum {Config.MAX_FILES_PER_BATCH} files allowed'
        }), 400
    
    uploaded_files = []
    job_id = str(uuid.uuid4())
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_format = get_file_format(filename)
            
            # Save file
            upload_path = os.path.join(Config.UPLOAD_FOLDER, job_id)
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            if file_size > Config.MAX_FILE_SIZE_MB * 1024 * 1024:
                os.remove(file_path)
                return jsonify({
                    'success': False,
                    'error': f'File {filename} exceeds {Config.MAX_FILE_SIZE_MB}MB limit'
                }), 400
            
            uploaded_files.append({
                'name': filename,
                'format': file_format,
                'size': file_size,
                'path': file_path
            })
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'files': uploaded_files
    })


@app.route('/api/translate', methods=['POST'])
def translate():
    """Start translation job"""
    data = request.json
    
    required_fields = ['job_id', 'source_lang', 'target_lang', 'service']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    job_id = data['job_id']
    
    # Get uploaded files
    upload_path = os.path.join(Config.UPLOAD_FOLDER, job_id)
    if not os.path.exists(upload_path):
        return jsonify({'success': False, 'error': 'Invalid job_id'}), 400
    
    files = []
    for filename in os.listdir(upload_path):
        file_path = os.path.join(upload_path, filename)
        files.append({
            'name': filename,
            'format': get_file_format(filename),
            'path': file_path
        })
    
    # Create translation job
    job = TranslationJob(
        job_id=job_id,
        files=files,
        source_lang=data['source_lang'],
        target_lang=data['target_lang'],
        service=data['service'],
        use_context=data.get('use_context', Config.USE_CONTEXT_PRESERVATION)
    )
    
    with translation_lock:
        translation_jobs[job_id] = job
    
    # Start processing in background
    thread = threading.Thread(target=process_translation_job, args=(job,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': 'Translation started'
    })


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id: str):
    """Get translation job status"""
    with translation_lock:
        job = translation_jobs.get(job_id)
    
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    return jsonify({
        'success': True,
        'job': job.to_dict()
    })


@app.route('/api/download/<job_id>', methods=['GET'])
def download_results(job_id: str):
    """Download translated files as ZIP"""
    with translation_lock:
        job = translation_jobs.get(job_id)
    
    if not job or job.status != 'completed':
        return jsonify({'success': False, 'error': 'Job not ready'}), 400
    
    # Create ZIP file
    zip_path = os.path.join(Config.OUTPUT_FOLDER, f"{job_id}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for result in job.results:
            if result.get('status') == 'completed':
                zipf.write(result['path'], result['translated_name'])
    
    return send_file(zip_path, as_attachment=True, download_name=f'translated_subtitles.zip')


@app.route('/api/edit/<job_id>', methods=['GET'])
def get_edit_data(job_id: str):
    """Get data for editing"""
    with translation_lock:
        job = translation_jobs.get(job_id)
    
    if not job or job.status != 'completed':
        return jsonify({'success': False, 'error': 'Job not ready'}), 400
    
    edit_data = []
    for result in job.results:
        if result.get('status') == 'completed':
            with open(result['path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries = SubtitleParser.parse(content.encode('utf-8'), 
                                          result['translated_name'].rsplit('.', 1)[1])
            
            edit_data.append({
                'filename': result['translated_name'],
                'entries': [entry.to_dict() for entry in entries]
            })
    
    return jsonify({
        'success': True,
        'files': edit_data
    })


@app.route('/api/save/<job_id>', methods=['POST'])
def save_edited(job_id: str):
    """Save edited subtitles"""
    data = request.json
    
    with translation_lock:
        job = translation_jobs.get(job_id)
    
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    try:
        for file_data in data['files']:
            filename = file_data['filename']
            entries_data = file_data['entries']
            
            # Find result
            result = next((r for r in job.results if r['translated_name'] == filename), None)
            if not result:
                continue
            
            # Create entries
            entries = [
                SubtitleEntry(
                    index=e['index'],
                    start_time=e['start_time'],
                    end_time=e['end_time'],
                    text=e['text']
                )
                for e in entries_data
            ]
            
            # Format and save
            file_format = filename.rsplit('.', 1)[1]
            content = SubtitleParser.format_output(entries, file_format)
            
            with open(result['path'], 'w', encoding='utf-8') as f:
                f.write(content)
        
        return jsonify({
            'success': True,
            'message': 'Files saved successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delete/<job_id>', methods=['DELETE'])
def delete_job(job_id: str):
    """Delete translation job and files"""
    with translation_lock:
        job = translation_jobs.pop(job_id, None)
    
    if job:
        # Delete upload folder
        upload_path = os.path.join(Config.UPLOAD_FOLDER, job_id)
        if os.path.exists(upload_path):
            import shutil
            shutil.rmtree(upload_path)
        
        # Delete output folder
        output_path = os.path.join(Config.OUTPUT_FOLDER, job_id)
        if os.path.exists(output_path):
            import shutil
            shutil.rmtree(output_path)
    
    return jsonify({
        'success': True,
        'message': 'Job deleted'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🎬 Subtitle Translator Pro - Starting Server")
    print("=" * 60)
    print(f"Server: http://localhost:{Config.PORT}")
    print(f"Available services: {', '.join(translation_engine.get_available_services())}")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.FLASK_DEBUG
    )
