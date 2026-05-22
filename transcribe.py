"""
TRANSCRIBE.PY
Multi-language audio transcription using OpenAI Whisper
Supports: English, Hindi, Marathi, and 96+ other languages
"""

import whisper
import os
import subprocess

# Set FFmpeg path for Whisper
ffmpeg_path = r"C:\Users\swapn\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = os.path.dirname(ffmpeg_path) + ";" + os.environ.get("PATH", "")

def transcribe_audio(audio_path, language="auto"):
    """
    Transcribe audio file to text
    
    Parameters:
        audio_path (str): Path to audio file
        language (str): Language code ("en", "hi", "mr", "auto")
        
    Returns:
        dict: {
            'text': full transcription,
            'segments': timestamped segments,
            'language': detected language code
        }
    """
    
    print("🎤 Loading Whisper model...")
    
    # Load Whisper model
    # Options: tiny, base, small, medium, large
    # base = good balance of speed and accuracy
    model = whisper.load_model("base")
    
    print(f"🔊 Transcribing audio: {os.path.basename(audio_path)}")
    print(f"   Language mode: {language}")
    
    # Transcribe
    result = model.transcribe(
        audio_path,
        language=None if language == "auto" else language,
        task="transcribe",
        verbose=False
    )
    
    detected_lang = result.get('language', 'unknown')
    
    # Language name mapping
    lang_names = {
        'en': 'English',
        'hi': 'Hindi (हिंदी)',
        'mr': 'Marathi (मराठी)',
        'ta': 'Tamil (தமிழ்)',
        'te': 'Telugu (తెలుగు)',
        'gu': 'Gujarati (ગુજરાતી)',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'ml': 'Malayalam (മലയാളം)',
        'pa': 'Punjabi (ਪੰਜਾਬੀ)',
        'bn': 'Bengali (বাংলা)'
    }
    
    print(f"✅ Transcription complete!")
    print(f"   Detected language: {lang_names.get(detected_lang, detected_lang)}")
    print(f"   Text length: {len(result['text'])} characters")
    
    return {
        'text': result['text'],
        'segments': result['segments'],
        'language': detected_lang
    }


# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TRANSCRIBE MODULE TEST")
    print("="*60 + "\n")
    
    # Test with a sample audio file
    test_audio = "uploads/sample.mp3"
    
    if os.path.exists(test_audio):
        result = transcribe_audio(test_audio)
        print("\n📝 Transcribed Text (first 300 chars):")
        print("-" * 60)
        print(result['text'][:300] + "...")
        print("-" * 60)
    else:
        print(f"❌ Test file not found: {test_audio}")
        print("   Please add a sample audio file to test.")