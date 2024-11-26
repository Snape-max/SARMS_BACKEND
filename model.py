from werkzeug.security import  generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('image_id', db.Integer, db.ForeignKey('image.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
    name = db.Column(db.String(20))  # 名字
    password = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    permission = db.Column(db.String(20))

    def __repr__(self):
        return '<User %r>' % self.name

    def __init__(self, name, password, email):
        self.name = name
        self.password = generate_password_hash(password)
        self.email = email
        self.permission = "user"

    def check_password(self, password):
        return check_password_hash(self.password, password)




class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img_path = db.Column(db.String(100))
    img_date = db.Column(db.DateTime)
    img_name = db.Column(db.String(30))
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('images', lazy='dynamic'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, img_path, img_date, img_name, author_id):
        self.img_path = img_path
        self.img_date = img_date
        self.img_name = img_name
        self.author_id = author_id

    def add_tags(self, tag_list):
        ...


    def get_images_by_author(self, author):
        return Image.query.filter_by(author_id=author).all()




class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))


