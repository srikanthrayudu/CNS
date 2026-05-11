import os
files = {
    "app.py": """from flask import Flask, render_template, request, jsonify
import os
from utils.model_trainer import train_model
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    file_path = os.path.join('dataset', file.filename)
    file.save(file_path)
    return jsonify({'success': 'File uploaded successfully', 'path': file_path})
@app.route('/train', methods=['POST'])
def train():
    data = request.json
    path = data.get('path')
    model_type = data.get('model_type', 'rf')
    res = train_model(path, model_type)
    return jsonify(res)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
""",
    "templates/index.html": """<!DOCTYPE html>
<html>
<head>
    <title>AI NIDS</title>
</head>
<body>
    <h1>Network Intrusion Detection System</h1>
    <a href="/dashboard">Go to Dashboard</a>
</body>
</html>
""",
    "templates/dashboard.html": """<!DOCTYPE html>
<html>
<head>
    <title>NIDS Dashboard</title>
</head>
<body>
    <h1>Dashboard</h1>
    <div>
        <h3>Upload Dataset</h3>
        <input type="file" id="dataset">
        <button onclick="uploadFile()">Upload</button>
    </div>
    <div>
        <h3>Train Model</h3>
        <button onclick="trainModel('rf')">Train Random Forest</button>
    </div>
    <div id="results"></div>
    <script>
        let uploadedPath = '';
        function uploadFile() {
            let formData = new FormData();
            formData.append("file", document.getElementById("dataset").files[0]);
            fetch('/upload', { method: "POST", body: formData })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    uploadedPath = data.path;
                    alert("Uploaded");
                }
            });
        }
        function trainModel(type) {
            fetch('/train', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: uploadedPath, model_type: type})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('results').innerText = JSON.stringify(data, null, 2);
            });
        }
    </script>
</body>
</html>
""",
    "README.md": """# AI-Based Network Intrusion Detection System (NIDS)
## Overview
This is a final-year mini project that uses Machine Learning to detect malicious network traffic.
## Setup
1. `pip install -r requirements.txt`
2. `python app.py`
## Usage
Upload a dataset (e.g., NSL-KDD csv format) and click train.
"""
}
for path, content in files.items():
    with open(path, 'w') as f:
        f.write(content)
