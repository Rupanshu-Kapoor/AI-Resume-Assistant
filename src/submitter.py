import os
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from flask import render_template, redirect, flash, request, url_for
from werkzeug.utils import secure_filename

class ResumeSubmitter:
    def __init__(self):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def upload_form(self):
        return render_template("upload_resume.html")

    def upload_file(self):
        if 'file' not in request.files:
            flash('No file part')
            return False
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return False
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash('File successfully uploaded')
            # return file path
            return os.path.join(UPLOAD_FOLDER, filename)
        else:
            flash('Allowed file types are pdf, doc, docx')
            return False
