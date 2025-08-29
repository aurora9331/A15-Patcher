from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

history = []

@app.route('/api/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    name = request.form.get('name')
    desc = request.form.get('desc')
    if not file or not name:
        return jsonify({'error': 'Eksik bilgi!'}), 400
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    entry = {'filename': filename, 'name': name, 'desc': desc, 'time': datetime.now().isoformat()}
    history.append(entry)
    return jsonify({'ok': True, 'entry': entry})

@app.route('/api/history')
def get_history():
    return jsonify(history[::-1])

@app.route('/uploads/<path:filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)