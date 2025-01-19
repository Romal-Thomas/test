from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import qrcode

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'qr_codes'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER

# Create folders if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Generate URL for the uploaded file
        viewer_url = f"http://127.0.0.1:5000/viewer?file={file.filename}"

        # Generate QR code for the URL
        qr_code_path = os.path.join(app.config['QR_FOLDER'], f"{file.filename}.png")
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(viewer_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')
        qr_img.save(qr_code_path)

        return jsonify({
            'file_url': viewer_url,
            'qr_code_url': f"/qr/{file.filename}.png",
            'filename': file.filename
        }), 200

@app.route('/uploads/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/qr/<filename>')
def serve_qr_code(filename):
    return send_from_directory(app.config['QR_FOLDER'], filename)

@app.route('/viewer')
def viewer():
    file = request.args.get('file')
    if not file:
        return "No file specified", 400
    return render_template('viewer.html', file=file)

if __name__ == '__main__':
    app.run(debug=True)
