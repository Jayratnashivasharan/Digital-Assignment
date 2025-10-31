from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folder to store uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip', 'rar'}


def allowed_file(filename):
    """Check file extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Homepage route."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        flash('No file part in the request.')
        return redirect(url_for('index'))

    file = request.files['file']
    name = request.form.get("name", "").strip()
    subject = request.form.get("subject", "").strip()

    if not name or not subject:
        flash('Please enter both Name and Subject.')
        return redirect(url_for('index'))

    if file.filename == '':
        flash('No file selected.')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        # Timestamp and safe filename
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_filename = f"{name}_{subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

        # Save file
        file.save(filepath)

        # Save submission info to log file
        log_file = os.path.join(app.config['UPLOAD_FOLDER'], "submissions.txt")
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"{name},{subject},{timestamp},{safe_filename}\n")

        flash('File uploaded successfully!')
        return render_template('success.html', name=name, subject=subject, filename=safe_filename)
    else:
        flash('Invalid file type. Please upload PDF, DOC, DOCX, ZIP, or RAR.')
        return redirect(url_for('index'))


@app.route('/submissions')
def submissions():
    """Show all uploaded submissions."""
    records = []
    log_file = os.path.join(app.config['UPLOAD_FOLDER'], "submissions.txt")

    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as log:
            for line in log.readlines():
                parts = line.strip().split(",")
                if len(parts) == 4:
                    name, subject, timestamp, filename = parts
                    records.append({
                        "name": name,
                        "subject": subject,
                        "timestamp": timestamp,
                        "filename": filename
                    })

    return render_template('submissions.html', records=records)


@app.route('/uploads/<path:filename>')
def download_file(filename):
    """Download uploaded file."""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash('File not found!')
        return redirect(url_for('submissions'))


if __name__ == '__main__':
    app.run(debug=True)
