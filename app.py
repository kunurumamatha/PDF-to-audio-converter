from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import pyttsx3
import PyPDF2

app = Flask(__name__)

# Define the upload folder for storing files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route to serve the uploaded audio files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404

# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Route for the form and conversion process
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error_message='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error_message='No selected file')

        # Save the file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Convert the PDF to audio
        try:
            text = extract_text_from_pdf(file_path)

            audio_filename = f'{file.filename.split(".")[0]}_audio.mp3'
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

            engine = pyttsx3.init()
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

            audio_url = f'/uploads/{audio_filename}'
            return render_template('index.html', audio_url=audio_url, success_message='Conversion successful!')

        except Exception as e:
            return render_template('index.html', error_message=f'Error during conversion: {str(e)}')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
