from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
import os
import pyttsx3
import pdfplumber

app = Flask(__name__)

# Configuration for file handling
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Helper function to check file extension
def allowed_file(filename):
    """Check if the file has a valid extension (PDF)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to extract text from the PDF
def pdf_to_text(file_path):
    """Extract text from a PDF file using pdfplumber."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages])
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# Function to convert text to audio
def text_to_audio(text, output_file):
    """Convert extracted text into audio using pyttsx3 and save to file."""
    try:
        engine = pyttsx3.init()
        engine.save_to_file(text, output_file)
        engine.runAndWait()
    except Exception as e:
        print(f"Error converting text to audio: {e}")
        return None

@app.route('/')
def index():
    """Render the home page with the form to upload a PDF."""
    return render_template("index.html")

@app.route('/convert', methods=['POST'])
def convert_pdf_to_audio():
    """Handle the file upload and conversion to audio."""
    try:
        # Check if 'pdf' key is in the request files
        if 'pdf' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        pdf = request.files['pdf']

        # If no file is selected
        if pdf.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Validate file extension
        if not allowed_file(pdf.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400

        # Secure and save the file
        filename = secure_filename(pdf.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf.save(file_path)

        # Extract text from the PDF
        text = pdf_to_text(file_path)
        if not text:
            return jsonify({'error': 'PDF has no readable text or failed to extract text'}), 400

        # Generate audio file
        output_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename.rsplit('.', 1)[0]}.mp3")
        text_to_audio(text, output_file)

        # Return the generated audio file as a download
        return send_file(output_file, as_attachment=True)

    except Exception as e:
        print(f"Error processing the request: {e}")
        return jsonify({'error': 'An error occurred on the server. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
