import json
import os
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.')
CORS(app)

DATA_FILE = 'bio_data.json'
UPLOAD_FOLDER = 'uploads'
ADMIN_PASSWORD = '1234'  # <-- เปลี่ยนรหัสผ่านเข้าหลังบ้านตรงนี้

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_DATA = {
    "name": "DEXTER",
    "bio": "Digital Creator & Developer | รับทำเว็บและบอท Discord",
    "status": "พร้อมรับงาน",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
    "theme": "dark",
    "effect": "particles",
    "socials": [
        {"platform": "discord", "url": "https://discord.com"},
        {"platform": "tiktok", "url": "https://tiktok.com"},
        {"platform": "instagram", "url": "https://instagram.com"}
    ],
    "links": [
        {"title": "เว็บไซต์ร้านค้าหลัก", "url": "https://example.com", "highlight": True},
        {"title": "ติดต่อสอบถาม / สั่งงาน", "url": "https://discord.com", "highlight": False}
    ]
}

def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 'effect' not in data:
            data['effect'] = 'particles'
        return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/bio', methods=['GET'])
def get_bio():
    return jsonify(load_data())

@app.route('/api/bio', methods=['POST'])
def update_bio():
    if request.headers.get('X-Admin-Key') != ADMIN_PASSWORD:
        return jsonify({"status": "error", "message": "รหัสผ่านแอดมินไม่ถูกต้อง"}), 401

    save_data(request.json)
    return jsonify({"status": "success", "message": "บันทึกข้อมูลเรียบร้อย"})

@app.route('/api/upload', methods=['POST'])
def upload_avatar():
    if request.headers.get('X-Admin-Key') != ADMIN_PASSWORD:
        return jsonify({"status": "error", "message": "รหัสผ่านไม่ถูกต้อง"}), 401

    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "ไม่พบไฟล์"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "ไม่ได้เลือกไฟล์"}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1] or '.png'
    filename = f"avatar_{int(time.time())}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({"status": "success", "url": f"/uploads/{filename}"})

if __name__ == '__main__':
    print("หน้าเว็บหลัก: http://localhost:3000")
    print("หน้าหลังบ้าน: http://localhost:3000/admin")
    app.run(host='0.0.0.0', port=3000, debug=True)
