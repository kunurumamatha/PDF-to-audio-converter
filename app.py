from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from gtts import gTTS
import os
import pdfplumber

# Initialize Flask app with template folder specified
app = Flask(__name__, template_folder='templates')

# Configuration for file handling
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Extract text from PDF
def pdf_to_text(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''.join([page.extract_text() or '' for page in pdf.pages])
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# Convert text to audio using gTTS
def text_to_audio(text, output_file):
    try:
        tts = gTTS(text)
        tts.save(output_file)
    except Exception as e:
        print(f"Error converting text to audio: {e}")
        return None

# Home page
@app.route('/')
def index():
    return render_template("index.html")

# PDF upload and conversion
@app.route('/convert', methods=['POST'])
def convert_pdf_to_audio():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        pdf = request.files['pdf']
        if pdf.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(pdf.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

        filename = secure_filename(pdf.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf.save(file_path)

        text = pdf_to_text(file_path)
        if not text:
            return jsonify({'error': 'PDF has no readable text or failed to extract text'}), 400

        output_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename.rsplit('.', 1)[0]}.mp3")
        text_to_audio(text, output_file)

        return send_file(output_file, as_attachment=True)

    except Exception as e:
        print(f"Error processing the request: {e}")
        return jsonify({'error': 'An error occurred on the server. Please try again later.'}), 500

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
