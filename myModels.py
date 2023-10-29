from db import db

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)