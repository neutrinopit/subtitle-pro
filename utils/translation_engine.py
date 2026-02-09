"""
Translation Engine Module
Handles integration with multiple translation services
"""

import time
import asyncio
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from deep_translator import GoogleTranslator, MyMemoryTranslator
import requests
import google.generativeai as genai

class TranslationService(ABC):
    """Abstract base class for translation services"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.rate_limit_delay = 0.1  # Default delay between requests
    
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source to target language"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if service is available"""
        pass
    
    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """Translate multiple texts with rate limiting"""
        results = []
        for text in texts:
            result = self.translate(text, source_lang, target_lang)
            results.append(result)
            time.sleep(self.rate_limit_delay)
        return results


class GoogleTranslateService(TranslationService):
    """Google Translate (Free) service"""
    
    def __init__(self):
        super().__init__()
        self.rate_limit_delay = 0.05  # Fast translation
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            if not text.strip():
                return text
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            print(f"Google Translate error: {str(e)}")
            return text
    
    def is_available(self) -> bool:
        try:
            GoogleTranslator(source='en', target='es').translate('test')
            return True
        except:
            return False


class YandexTranslateService(TranslationService):
    """Yandex Translate service"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.rate_limit_delay = 0.1
        self.base_url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            if not text.strip() or not self.api_key:
                return text
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "sourceLanguageCode": source_lang,
                "targetLanguageCode": target_lang,
                "texts": [text]
            }
            
            response = requests.post(self.base_url, json=data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                return result['translations'][0]['text']
            return text
        except Exception as e:
            print(f"Yandex Translate error: {str(e)}")
            return text
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class GeminiTranslateService(TranslationService):
    """Google Gemini API service with context awareness"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.rate_limit_delay = 0.2
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
    
    def translate(self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None) -> str:
        try:
            if not text.strip() or not self.api_key:
                return text
            
            prompt = f"Translate the following text from {source_lang} to {target_lang}. "
            prompt += "Provide ONLY the translation without explanations or additional text.\n\n"
            
            if context:
                prompt += f"Context from previous subtitles:\n{context}\n\n"
            
            prompt += f"Text to translate:\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Translate error: {str(e)}")
            return text
    
    def translate_with_context(self, texts: List[str], source_lang: str, target_lang: str, 
                              context_window: int = 3) -> List[str]:
        """Translate with context awareness"""
        results = []
        for i, text in enumerate(texts):
            # Get context from previous translations
            context = None
            if i > 0:
                start_idx = max(0, i - context_window)
                context_texts = results[start_idx:i]
                context = " ".join(context_texts[-context_window:])
            
            result = self.translate(text, source_lang, target_lang, context)
            results.append(result)
            time.sleep(self.rate_limit_delay)
        
        return results
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class DeepLTranslateService(TranslationService):
    """DeepL API service"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.rate_limit_delay = 0.15
        self.base_url = "https://api-free.deepl.com/v2/translate"
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        try:
            if not text.strip() or not self.api_key:
                return text
            
            data = {
                'auth_key': self.api_key,
                'text': text,
                'source_lang': source_lang.upper(),
                'target_lang': target_lang.upper()
            }
            
            response = requests.post(self.base_url, data=data)
            if response.status_code == 200:
                result = response.json()
                return result['translations'][0]['text']
            return text
        except Exception as e:
            print(f"DeepL Translate error: {str(e)}")
            return text
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class TranslationEngine:
    """Main translation engine managing multiple services"""
    
    def __init__(self, gemini_api_key: Optional[str] = None, deepl_api_key: Optional[str] = None):
        self.services = {
            'google': GoogleTranslateService(),
            'gemini': GeminiTranslateService(gemini_api_key),
            'deepl': DeepLTranslateService(deepl_api_key),
        }
        
        self.default_service = 'google'
    
    def get_available_services(self) -> List[str]:
        """Get list of available translation services"""
        return [name for name, service in self.services.items() if service.is_available()]
    
    def translate(self, text: str, source_lang: str, target_lang: str, 
                 service_name: str = 'google') -> str:
        """Translate text using specified service"""
        service = self.services.get(service_name, self.services[self.default_service])
        return service.translate(text, source_lang, target_lang)
    
    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str,
                       service_name: str = 'google', use_context: bool = False,
                       context_window: int = 3) -> List[str]:
        """Batch translate with optional context preservation"""
        service = self.services.get(service_name, self.services[self.default_service])
        
        # Use context-aware translation for Gemini
        if service_name == 'gemini' and use_context and isinstance(service, GeminiTranslateService):
            return service.translate_with_context(texts, source_lang, target_lang, context_window)
        
        return service.batch_translate(texts, source_lang, target_lang)
    
    def add_custom_service(self, name: str, service: TranslationService):
        """Add a custom translation service"""
        self.services[name] = service
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all services"""
        return {
            name: {
                'available': service.is_available(),
                'type': 'free' if name in ['google'] else 'paid',
                'supports_context': isinstance(service, GeminiTranslateService)
            }
            for name, service in self.services.items()
        }
