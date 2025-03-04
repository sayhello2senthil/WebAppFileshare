###


# A Simple Python Web App for file sharing between linux and windows on local network
# 1.) The UI should be simple with ability to drag and drop files into it
# 2.) The UI should allow to simply download the files when accessing using the browser
# 
# 
# f###

from flask import Flask, request, send_from_directory, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>File Sharing</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        .drop-zone {
            width: 80%;
            max-width: 600px;
            height: 200px;
            border: 2px dashed #aaa;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            font-size: 18px;
            color: #555;
            cursor: pointer;
        }
        .file-list { margin-top: 20px; }
        .file-list a { display: block; margin: 5px; }
    </style>
</head>
<body>
    <h1>File Sharing</h1>
    <div class='drop-zone' id='drop-zone'>Drag & Drop files here or Click to Upload</div>
    <input type='file' id='file-input' multiple style='display: none;'>
    <div class='file-list'>
        <h2>Uploaded Files</h2>
        {% for file in files %}
            <a href='/uploads/{{ file }}' download>{{ file }}</a>
        {% endfor %}
    </div>
    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#000';
        });
        dropZone.addEventListener('dragleave', () => dropZone.style.borderColor = '#aaa');
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#aaa';
            uploadFiles(e.dataTransfer.files);
        });
        fileInput.addEventListener('change', () => uploadFiles(fileInput.files));
        
        function uploadFiles(files) {
            for (let file of files) {
                let formData = new FormData();
                formData.append('file', file);
                fetch('/upload', { method: 'POST', body: formData })
                    .then(response => response.text())
                    .then(() => location.reload())
                    .catch(error => console.error('Upload failed:', error));
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        if file.content_length > MAX_FILE_SIZE:
            return 'File too large', 413
        file.save(file_path)
        return 'File uploaded successfully', 200
    return 'No file selected', 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
