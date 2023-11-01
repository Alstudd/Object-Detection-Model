# python -m venv env: python virtual environment

from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for, Response
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess

from db import db_init, db
from myModels import Img

app = Flask(__name__)

app.static_folder = 'static'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

uploads_dir = os.path.join('instance/', 'uploads')

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

    # subprocess.run("ls")
    command1 = f'python3 detect.py --source {os.path.join(uploads_dir, secure_filename(mainFile.filename))}'
    subprocess.run(command1, shell=True)
    # subprocess.run(['python', 'detect.py', '--source', os.path.join(uploads_dir, secure_filename(mainFile.filename))], shell=True)
    
    fileName = secure_filename(mainFile.filename)
    mimeType = mainFile.mimetype
    if not fileName or not mimeType:
        return 'Bad upload!', 400

    uploadedFile = Img(img=open(os.path.join(uploads_dir, secure_filename(mainFile.filename)), 'rb').read(), name=fileName, mimetype=mimeType)
    db.session.add(uploadedFile)
    db.session.commit()

    return fileName

@app.route("/opencam", methods=['GET', 'POST'])
def opencam():
    print("Webcam turned on!")
    command2 = f'python3 detect.py --source 0'
    subprocess.run(command2, shell=True)
    # subprocess.run(['python', 'detect.py', '--source', '0'], shell=True)
    return "done"

# @app.route('/<int:id>')
# def get_file(id):
#     uploadedFile = Img.query.filter_by(id=id).first()
#     if not uploadedFile:
#         return 'File Not Found!', 404
#     return Response(uploadedFile.img, mimetype=uploadedFile.mimetype)
