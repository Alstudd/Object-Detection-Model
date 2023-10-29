# python -m venv env: python virtual environment

from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess

app = Flask(__name__)

uploads_dir = os.path.join(app.instance_path, 'uploads')

os.makedirs(uploads_dir, exist_ok=True)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/detect", methods=['GET', 'POST'])
def detect():
    if not request.method == "POST":
        return
    video = request.files['video']
    video.save(os.path.join(uploads_dir, secure_filename(video.filename)))
    print(video)
    # subprocess.run("ls")
    command1 = f'python3 detect.py --source {os.path.join(uploads_dir, secure_filename(video.filename))}'
    subprocess.run(command1, shell=True)

    obj = secure_filename(video.filename)
    return obj

@app.route("/opencam", methods=['GET', 'POST'])
def opencam():
    print("Webcam turned on!")
    command2 = f'python3 detect.py --source 0'
    subprocess.run(command2, shell=True)
    return "done"
