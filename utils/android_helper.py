"""
Android Integration Module
This module provides helper functions for Android app integration
"""

from flask import jsonify
from typing import Dict, Any

class AndroidAPI:
    """Helper class for Android-specific API endpoints"""
    
    @staticmethod
    def format_response(success: bool, data: Any = None, error: str = None) -> Dict:
        """Format response for Android app"""
        response = {
            'success': success,
            'timestamp': int(time.time())
        }
        
        if data:
            response['data'] = data
        
        if error:
            response['error'] = error
        
        return response
    
    @staticmethod
    def validate_request(request_data: Dict, required_fields: list) -> tuple:
        """Validate request from Android app"""
        missing_fields = []
        
        for field in required_fields:
            if field not in request_data:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing fields: {', '.join(missing_fields)}"
        
        return True, None


# Android App Configuration
ANDROID_CONFIG = {
    'min_version': '1.0.0',
    'api_version': 'v1',
    'max_upload_size': 1048576,  # 1MB in bytes
    'max_files_per_batch': 20,
    'supported_formats': ['srt', 'vtt', 'ass', 'sub', 'sbv', 'stl'],
    'supported_languages': [
        'ar', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru',
        'zh', 'ja', 'ko', 'tr', 'hi', 'nl', 'pl', 'sv'
    ],
    'features': {
        'context_preservation': True,
        'batch_translation': True,
        'offline_editor': True,
        'cloud_sync': True
    }
}


def get_android_config():
    """Get configuration for Android app"""
    return AndroidAPI.format_response(True, data=ANDROID_CONFIG)
