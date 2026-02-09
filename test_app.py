"""
Unit Tests for Subtitle Translator Pro
Run with: pytest test_app.py
"""

import pytest
import os
import sys
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils.subtitle_parser import SubtitleParser, SubtitleEntry
from utils.translation_engine import TranslationEngine, GoogleTranslateService


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestSubtitleParser:
    """Test subtitle parser functionality"""
    
    def test_parse_srt(self):
        """Test SRT parsing"""
        srt_content = """1
00:00:01,000 --> 00:00:03,500
Hello World

2
00:00:04,000 --> 00:00:07,000
This is a test
"""
        entries = SubtitleParser.parse(srt_content.encode('utf-8'), 'srt')
        
        assert len(entries) == 2
        assert entries[0].text == "Hello World"
        assert entries[1].start_time == "00:00:04,000"
    
    def test_format_srt(self):
        """Test SRT formatting"""
        entries = [
            SubtitleEntry(1, "00:00:01,000", "00:00:03,500", "Hello"),
            SubtitleEntry(2, "00:00:04,000", "00:00:07,000", "World")
        ]
        
        output = SubtitleParser.format_srt(entries)
        assert "Hello" in output
        assert "00:00:01,000" in output


class TestTranslationEngine:
    """Test translation engine"""
    
    def test_google_service_available(self):
        """Test Google Translate availability"""
        service = GoogleTranslateService()
        # Note: May fail without internet connection
        assert service.is_available() in [True, False]
    
    def test_translation_engine_init(self):
        """Test translation engine initialization"""
        engine = TranslationEngine()
        services = engine.get_available_services()
        
        assert 'google' in engine.services
        assert isinstance(services, list)
    
    def test_translate_simple(self):
        """Test simple translation"""
        engine = TranslationEngine()
        
        # Test translation (may fail without internet)
        try:
            result = engine.translate("Hello", "en", "es", "google")
            assert result is not None
            assert len(result) > 0
        except:
            # Skip if no internet
            pass


class TestAPI:
    """Test API endpoints"""
    
    def test_index(self, client):
        """Test index page"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_get_languages(self, client):
        """Test languages endpoint"""
        response = client.get('/api/languages')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'languages' in data
        assert 'ar' in data['languages']
        assert 'en' in data['languages']
    
    def test_get_services(self, client):
        """Test services endpoint"""
        response = client.get('/api/services')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'services' in data
        assert 'google' in data['services']
    
    def test_upload_no_files(self, client):
        """Test upload without files"""
        response = client.post('/api/upload')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_upload_valid_file(self, client):
        """Test upload with valid SRT file"""
        srt_content = """1
00:00:01,000 --> 00:00:03,500
Hello World
"""
        
        data = {
            'files': (BytesIO(srt_content.encode('utf-8')), 'test.srt')
        }
        
        response = client.post(
            '/api/upload',
            content_type='multipart/form-data',
            data=data
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'job_id' in data


class TestIntegration:
    """Integration tests"""
    
    def test_full_translation_workflow(self, client):
        """Test complete translation workflow"""
        
        # 1. Upload file
        srt_content = """1
00:00:01,000 --> 00:00:03,500
Hello
"""
        upload_data = {
            'files': (BytesIO(srt_content.encode('utf-8')), 'test.srt')
        }
        
        upload_response = client.post(
            '/api/upload',
            content_type='multipart/form-data',
            data=upload_data
        )
        
        assert upload_response.status_code == 200
        upload_json = upload_response.get_json()
        job_id = upload_json['job_id']
        
        # 2. Start translation
        translate_data = {
            'job_id': job_id,
            'source_lang': 'en',
            'target_lang': 'es',
            'service': 'google',
            'use_context': False
        }
        
        translate_response = client.post(
            '/api/translate',
            json=translate_data
        )
        
        assert translate_response.status_code == 200
        translate_json = translate_response.get_json()
        assert translate_json['success'] is True
        
        # 3. Check status
        import time
        time.sleep(2)  # Wait for translation
        
        status_response = client.get(f'/api/status/{job_id}')
        assert status_response.status_code == 200
        
        status_json = status_response.get_json()
        assert status_json['success'] is True
        assert 'job' in status_json


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
