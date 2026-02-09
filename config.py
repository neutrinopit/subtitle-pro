import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '')
    
    # Server Settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Translation Settings
    MAX_FILES_PER_BATCH = int(os.getenv('MAX_FILES_PER_BATCH', 20))
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 1))
    REQUEST_RATE_LIMIT = int(os.getenv('REQUEST_RATE_LIMIT', 100))
    RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', 60))
    
    # Context Settings
    CONTEXT_WINDOW_SIZE = int(os.getenv('CONTEXT_WINDOW_SIZE', 5))
    USE_CONTEXT_PRESERVATION = os.getenv('USE_CONTEXT_PRESERVATION', 'True').lower() == 'true'
    
    # Supported Formats
    SUPPORTED_FORMATS = ['.srt', '.vtt', '.stl', '.sbv', '.sub', '.ass']
    
    # Upload Settings
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
    ALLOWED_EXTENSIONS = {'srt', 'vtt', 'stl', 'sbv', 'sub', 'ass'}
