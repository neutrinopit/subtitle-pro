import streamlit as st
import os
import json
import zipfile
import io
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.subtitle_parser import SubtitleParser
from utils.translation_engine import TranslationEngine
from config import Config

# --- إعدادات صفحة Streamlit ---
st.set_page_config(page_title="Subtitle Translator Pro", layout="wide")

# --- تهيئة التطبيق (Flask) ---
app = Flask(__name__)
CORS(app)
translation_engine = TranslationEngine()

# --- دالة المساعدة للترجمة (تستخدم من Flask و Streamlit) ---
def process_translation(file_content, filename, target_lang, service, api_key=None):
    parser = SubtitleParser()
    subtitles = parser.parse(file_content, filename)
    if not subtitles:
        return None
    
    translated_subtitles = translation_engine.translate(
        subtitles, target_lang, service, api_key
    )
    return parser.format(translated_subtitles, filename)

# --- واجهة Streamlit (للتشغيل على Streamlit Cloud) ---
def run_streamlit_interface():
    st.title("🎬 Subtitle Translator Pro")
    st.markdown("### ترجمة احترافية لملفات الترجمة بسرعة البرق")

    with st.sidebar:
        st.header("⚙️ الإعدادات")
        service = st.selectbox("خدمة الترجمة", ["google", "gemini", "deepl", "yandex"])
        target_lang = st.text_input("لغة الهدف (رمز اللغة مثل 'ar')", "ar")
        api_key = st.text_input("API Key (إذا لزم الأمر)", type="password")

    uploaded_files = st.file_uploader("اختر ملفات الترجمة", accept_multiple_files=True)

    if st.button("🚀 بدء الترجمة"):
        if not uploaded_files:
            st.error("الرجاء رفع ملف واحد على الأقل")
            return

        results = []
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            with st.status(f"جاري معالجة {uploaded_file.name}...", expanded=True):
                content = uploaded_file.read().decode("utf-8")
                translated_content = process_translation(content, uploaded_file.name, target_lang, service, api_key)
                
                if translated_content:
                    results.append((uploaded_file.name, translated_content))
                    st.success(f"تمت ترجمة {uploaded_file.name}")
                else:
                    st.error(f"فشل في ترجمة {uploaded_file.name}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        if results:
            if len(results) == 1:
                st.download_button(
                    label="📥 تحميل الملف المترجم",
                    data=results[0][1],
                    file_name=f"translated_{results[0][0]}",
                    mime="text/plain"
                )
            else:
                # إنشاء ملف ZIP للملفات المتعددة
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for name, content in results:
                        zip_file.writestr(f"translated_{name}", content)
                
                st.download_button(
                    label="📥 تحميل الكل (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="translated_subtitles.zip",
                    mime="application/zip"
                )

# --- مسارات Flask (للتوافق مع التطبيقات الأخرى) ---
@app.route('/translate', methods=['POST'])
def translate_api():
    data = request.json
    # منطق الـ API الخاص بك هنا (موجود في الكود الأصلي)
    return jsonify({"status": "success", "message": "API is active"})

# --- تشغيل التطبيق ---
if __name__ == "__main__":
    # إذا تم تشغيل الملف بواسطة Streamlit، سيتم تشغيل الواجهة الرسومية
    # وإلا سيتم تشغيل خادم Flask (للاستضافة على Render/Heroku)
    try:
        # محاولة التحقق إذا كنا داخل بيئة Streamlit
        import streamlit.runtime.scriptrunner as sr
        run_streamlit_interface()
    except:
        # تشغيل Flask كخيار احتياطي أو عند التشغيل المباشر
        print("Starting Flask Server...")
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
else:
    # هذا الجزء يضمن عمل الواجهة عند رفعها على Streamlit Cloud
    run_streamlit_interface()

