import os
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from utils.subtitle_parser import SubtitleParser
from utils.translation_engine import TranslationEngine
from config import Config

# إعداد Flask ليشير إلى المجلد الصحيح للقوالب (Templates)
app = Flask(__name__, 
            template_folder='.', # يبحث عن index.html في المجلد الرئيسي
            static_folder='.')   # يبحث عن ملفات CSS/JS في المجلد الرئيسي

CORS(app)
translation_engine = TranslationEngine()

# --- المسارات (Routes) ---

@app.route('/')
def index():
    # هذا السطر هو الذي سيقوم بتشغيل الـ Template الخاص بك
    return send_file('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        target_lang = request.form.get('target_lang', 'ar')
        service = request.form.get('service', 'google')
        api_key = request.form.get('api_key')

        content = file.read().decode('utf-8')
        parser = SubtitleParser()
        subtitles = parser.parse(content, file.filename)

        if not subtitles:
            return jsonify({"error": "Failed to parse subtitle"}), 400

        translated = translation_engine.translate(subtitles, target_lang, service, api_key)
        result = parser.format(translated, file.filename)

        return jsonify({
            "success": True,
            "translated_content": result,
            "filename": f"translated_{file.filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- حل مشكلة الاستضافة على Streamlit ---

if __name__ == "__main__":
    # تشغيل السيرفر بالطريقة التقليدية
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

# ملاحظة: إذا كنت تستخدم Streamlit Cloud، سيظل هناك تعارض لأن المنصة لا تدعم Flask كخادم ويب أساسي بسهولة.
# هذا الكود سيعمل بامتياز على Render أو PythonAnywhere أو أي سيرفر حقيقي.

