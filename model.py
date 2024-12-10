from sqlalchemy.orm import aliased
from werkzeug.security import  generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import uuid
from sqlalchemy.dialects.postgresql import UUID
from utils import CATEGORIES

db = SQLAlchemy()


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


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    @staticmethod
    def get_images_by_tag(tag_name: str):
        # 使用别名来避免命名冲突
        image_alias = aliased(Image)

        # 获取与指定标签名匹配的标签ID
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            return []  # 如果没有找到匹配的标签，则返回空列表

        # 查询所有与该标签关联的图片
        images = db.session.query(image_alias). \
            join(ImageTag, ImageTag.image_id == image_alias.id). \
            filter(ImageTag.tag_id == tag.id).all()

        return images


class ImageTag(db.Model):
    __tablename__ = 'tags'
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    image_id = db.Column(UUID(as_uuid=True), db.ForeignKey('image.id'), primary_key=True, default=uuid.uuid4)
    num = db.Column(db.Integer)

    # 定义与Tag和Image的关系
    tag = db.relationship('Tag', backref=db.backref('image_associations', cascade='all, delete-orphan'))
    image = db.relationship('Image', backref=db.backref('tag_associations', cascade='all, delete-orphan'))


class Image(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    img_url = db.Column(db.String(100))
    img_date = db.Column(db.DateTime)
    img_name = db.Column(db.String(30))
    is_labeled = db.Column(db.Boolean)
    labeled_image_url = db.Column(db.String(100))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, img_date, img_name, author_id, is_labeled):
        self.img_date = img_date
        self.img_name = img_name
        self.author_id = author_id
        self.is_labeled = is_labeled


    def add_tags(self, tag_dict: dict):
        for tid, num in tag_dict.items():
            tag_image = ImageTag(tag_id=tid, image_id=self.id, num=num)
            db.session.add(tag_image)


    @staticmethod
    def get_images_by_author(author):
        return Image.query.filter_by(author_id=author).all()


    def __get_tags(self):
        if not self.is_labeled:
            return {}
        tags =  ImageTag.query.filter_by(image_id=self.id).all()
        tags_dict = {}
        for tag in tags:
            tid = tag.tag_id
            tag_name = Tag.query.filter_by(id=tid).first().name
            tags_dict[tag_name] = tag.num
        return tags_dict


    def serialize(self):
        return {
            'id': str(self.id),
            'img_url': self.img_url,
            'img_date': self.img_date.isoformat() if self.img_date else None,  # 确保日期格式化为字符串
            'img_name': self.img_name,
            'labeled_image_url': self.labeled_image_url,
            'tags': self.__get_tags(),
        }

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    md5 = db.Column(db.String(32))
    path = db.Column(db.String(100))








def initialize_tags():
    # 检查 Tag 表中是否有数据
    if not Tag.query.first():
        # 插入 CATEGORIES 中的数据
        for category_id, category_name in CATEGORIES.items():
            new_tag = Tag(name=category_name, id=category_id)
            db.session.add(new_tag)
        db.session.commit()
        print("Tags initialized successfully!")
    else:
        print("Tags already exist.")