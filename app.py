# python -m venv env: python virtual environment

from io import BytesIO
from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for, Response
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess

from db import db_init, db
from myModels import Img

import base64

app = Flask(__name__)

app.static_folder = 'static'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

uploads_dir = os.path.join(app.instance_path, 'uploads')

os.makedirs(uploads_dir, exist_ok=True)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/detect", methods=['GET', 'POST'])
def detect():
    if not request.method == "POST":
        return
    mainFile = request.files['video']
    if not mainFile:
        return 'No file uploaded!'
    mainFile.save(os.path.join(uploads_dir, secure_filename(mainFile.filename)))
    print(mainFile)

    # image to url
    with open(os.path.join(uploads_dir, secure_filename(mainFile.filename)), "rb") as image_file:
        image_data = image_file.read()
        base64_data = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:{mainFile.mimetype};base64,{base64_data}"

    # subprocess.run("ls")
    # command1 = f'python3 detect.py --source {os.path.join(uploads_dir, secure_filename(mainFile.filename))}'
    # subprocess.run(command1, shell=True)
    subprocess.run(['python', 'detect.py', '--source', os.path.join(uploads_dir, secure_filename(mainFile.filename))], shell=True)
    
    fileName = secure_filename(mainFile.filename)
    mimeType = mainFile.mimetype
    if not fileName or not mimeType:
        return 'Bad upload!', 400

    uploadedFile = Img(img=image_data, name=fileName, mimetype=mimeType, imgURL=data_url)
    db.session.add(uploadedFile)
    db.session.commit()

    return fileName

@app.route("/opencam", methods=['GET', 'POST'])
def opencam():
    print("Webcam turned on!")
    # command2 = f'python3 detect.py --source 0'
    # subprocess.run(command2, shell=True)
    subprocess.run(['python', 'detect.py', '--source', '0'], shell=True)
    return "done"

@app.route('/<int:id>')
def get_file(id):
    uploadedFile = Img.query.filter_by(id=id).first()
    if not uploadedFile:
        return 'File Not Found!', 404
    return Response(uploadedFile.img, mimetype=uploadedFile.mimetype)

@app.route('/display/<int:id>')
def display_file(id):
    uploadedFile = Img.query.filter_by(id=id).first()
    if not uploadedFile:
        return 'File Not Found!', 404 
    return send_file(BytesIO(uploadedFile.img), mimetype=uploadedFile.mimetype, download_name=uploadedFile.name)

@app.route('/download/<int:id>')
def download_file(id):
    uploadedFile = Img.query.filter_by(id=id).first()
    if not uploadedFile:
        return 'File Not Found!', 404 
    return send_file(BytesIO(uploadedFile.img), mimetype=uploadedFile.mimetype, download_name=uploadedFile.name, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080', debug=True)