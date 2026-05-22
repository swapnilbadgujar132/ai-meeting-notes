"""
APP.PY
Main Flask web application
Multi-language AI Meeting Notes Generator
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime

# Import our modules
from transcribe import transcribe_audio
from summarize import MeetingSummarizer
from extract_actions import ActionExtractor
from pdf_generator import PDFGenerator

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Allowed audio formats
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'webm'}

# Create required folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Initialize components (load models once at startup)
print("\n" + "="*70)
print("🚀 INITIALIZING AI MEETING NOTES GENERATOR")
print("="*70 + "\n")

print("Loading AI models... (this may take 1-2 minutes on first run)")
summarizer = MeetingSummarizer()
action_extractor = ActionExtractor()
pdf_generator = PDFGenerator()

print("\n" + "="*70)
print("✅ ALL SYSTEMS READY!")
print("="*70 + "\n")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        # Validate file presence
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['audio_file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file format. Supported: {", ".join(ALLOWED_EXTENSIONS).upper()}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        
        print("\n" + "="*70)
        print(f"🎤 PROCESSING: {filename}")
        print(f"   File size: {file_size:.2f} MB")
        print("="*70 + "\n")
        
        # ===== STEP 1: TRANSCRIPTION =====
        print("STEP 1/4: TRANSCRIPTION")
        print("-" * 70)
        transcription_result = transcribe_audio(filepath, language="auto")
        full_text = transcription_result['text']
        detected_lang = transcription_result.get('language', 'en')
        
        # Language display names
        lang_display = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'mr': 'Marathi (मराठी)',
            'ta': 'Tamil (தமிழ்)',
            'te': 'Telugu (తెలుగు)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'bn': 'Bengali (বাংলা)',
            'ur': 'Urdu (اردو)'
        }
        
        language_name = lang_display.get(detected_lang, detected_lang.upper())
        
        # ===== STEP 2: SUMMARIZATION =====
        print("\n" + "-" * 70)
        print("STEP 2/4: SUMMARIZATION")
        print("-" * 70)
        summary = summarizer.summarize_text(full_text, language=detected_lang)
        
        # ===== STEP 3: ACTION EXTRACTION =====
        print("\n" + "-" * 70)
        print("STEP 3/4: ACTION & DECISION EXTRACTION")
        print("-" * 70)
        actions = action_extractor.extract_action_items(full_text, language=detected_lang)
        decisions = action_extractor.extract_decisions(full_text, language=detected_lang)
        
        # ===== STEP 4: PDF GENERATION =====
        print("\n" + "-" * 70)
        print("STEP 4/4: PDF GENERATION")
        print("-" * 70)
        pdf_filename = f"meeting_notes_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        # Prepare meeting data
        meeting_data = {
            'date': datetime.now().strftime('%B %d, %Y'),
            'duration': f"{len(full_text.split()) // 150} minutes (estimated)",
            'language': language_name,
            'summary': summary,
            'actions': actions,
            'decisions': decisions,
            'full_text': full_text
        }
        
        pdf_generator.generate_report(pdf_path, meeting_data)
        
        # Cleanup: Delete uploaded audio file
        try:
            os.remove(filepath)
            print(f"   🗑️  Cleaned up temporary audio file")
        except:
            pass
        
        print("\n" + "="*70)
        print("✅ PROCESSING COMPLETE!")
        print("="*70 + "\n")
        
        # Return success response
        return jsonify({
            'success': True,
            'pdf_url': f'/download/{pdf_filename}',
            'pdf_filename': pdf_filename,
            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
            'actions_count': len(actions),
            'decisions_count': len(decisions),
            'detected_language': language_name,
            'word_count': len(full_text.split())
        })
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if 'filepath' in locals():
            try:
                os.remove(filepath)
            except:
                pass
        
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated PDF"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': True,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎤 AI MEETING NOTES GENERATOR")
    print("   Multi-language Support: English, Hindi, Marathi + 96 more")
    print("="*70)
    print("\n🌐 Server starting...")
    print("   URL: http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)