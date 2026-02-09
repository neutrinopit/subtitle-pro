"""
Quick Translation Demo
A simple script to demonstrate fast translation capabilities
"""

from utils.translation_engine import TranslationEngine, GoogleTranslateService
from utils.subtitle_parser import SubtitleParser
import time

def demo_fast_translation():
    """Demonstrate fast translation like Google Translate Web"""
    
    print("=" * 60)
    print("🎬 Subtitle Translator Pro - Fast Translation Demo")
    print("=" * 60)
    print()
    
    # Sample subtitle content
    sample_srt = """1
00:00:01,000 --> 00:00:03,500
Welcome to our movie

2
00:00:04,000 --> 00:00:07,000
This is an amazing story

3
00:00:08,000 --> 00:00:11,500
About friendship and adventure

4
00:00:12,000 --> 00:00:15,000
Join us on this journey

5
00:00:16,000 --> 00:00:19,500
You won't regret it
"""
    
    print("📝 Sample Subtitle (English):")
    print("-" * 60)
    print(sample_srt)
    print()
    
    # Parse
    print("🔍 Parsing subtitle...")
    entries = SubtitleParser.parse(sample_srt.encode('utf-8'), 'srt')
    print(f"✅ Parsed {len(entries)} entries")
    print()
    
    # Translate with Google (Fast)
    print("⚡ Translating with Google Translate (Fast Mode)...")
    print("-" * 60)
    
    engine = TranslationEngine()
    texts = [entry.text for entry in entries]
    
    start_time = time.time()
    translated_texts = engine.batch_translate(
        texts=texts,
        source_lang='en',
        target_lang='ar',
        service_name='google'
    )
    end_time = time.time()
    
    duration = end_time - start_time
    
    print()
    print("📄 Translated Results (Arabic):")
    print("-" * 60)
    for i, (original, translated) in enumerate(zip(texts, translated_texts), 1):
        print(f"{i}. {original}")
        print(f"   → {translated}")
        print()
    
    print("=" * 60)
    print(f"⏱️  Translation Time: {duration:.2f} seconds")
    print(f"⚡ Average per line: {duration/len(texts):.3f} seconds")
    print(f"🚀 Speed: {len(texts)/duration:.1f} lines/second")
    print("=" * 60)
    print()
    
    # Create translated SRT
    print("💾 Creating translated SRT file...")
    translated_entries = []
    for entry, translated_text in zip(entries, translated_texts):
        from utils.subtitle_parser import SubtitleEntry
        translated_entry = SubtitleEntry(
            index=entry.index,
            start_time=entry.start_time,
            end_time=entry.end_time,
            text=translated_text
        )
        translated_entries.append(translated_entry)
    
    output_srt = SubtitleParser.format_srt(translated_entries)
    
    print("✅ Translated SRT:")
    print("-" * 60)
    print(output_srt)
    print()
    
    # Save to file
    with open('demo_translated.srt', 'w', encoding='utf-8') as f:
        f.write(output_srt)
    
    print("✅ Saved to: demo_translated.srt")
    print()
    
    print("🎉 Demo completed successfully!")
    print()
    print("💡 Key Features Demonstrated:")
    print("  ✓ Fast parsing of SRT format")
    print("  ✓ Instant translation with Google Translate")
    print("  ✓ Batch processing for speed")
    print("  ✓ Proper SRT formatting")
    print("  ✓ Arabic text support")
    print()


if __name__ == '__main__':
    try:
        demo_fast_translation()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        print("⚠️ Make sure you have internet connection for translation")
