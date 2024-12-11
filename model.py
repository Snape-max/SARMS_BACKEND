from datetime import datetime, timedelta

from sqlalchemy import func, and_
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
    def get_images_by_tags(tag_names: list):
        if not tag_names:
            # 如果标签列表为空，则返回一个空的查询对象
            return Image.query.filter(False)

        # 获取与指定标签名匹配的标签ID列表
        tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
        if not tags:
            return Image.query.filter(False)  # 如果没有找到匹配的标签，则返回空查询对象

        tag_ids = [tag.id for tag in tags]

        # 使用别名来避免命名冲突
        image_alias = aliased(Image)

        # 查询所有与这些标签关联的图片
        images_query = db.session.query(image_alias). \
            join(ImageTag, ImageTag.image_id == image_alias.id). \
            filter(ImageTag.tag_id.in_(tag_ids))

        return images_query


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
    img_md5 = db.Column(db.String(50))
    img_name = db.Column(db.String(30))
    is_labeled = db.Column(db.Boolean)
    labeled_image_url = db.Column(db.String(100))
    labeled_image_md5 = db.Column(db.String(50))
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
        author_name = User.query.filter_by(id=self.author_id).first().name
        return {
            'id': str(self.id),
            'img_url': self.img_url,
            'img_date': self.img_date.isoformat() if self.img_date else None,  # 确保日期格式化为字符串
            'img_name': self.img_name,
            'labeled_image_url': self.labeled_image_url,
            'author': author_name,
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


def generate_date_series(start_date, end_date):
    """生成从开始日期到结束日期的日期序列"""
    delta = end_date - start_date
    return [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]

def count_image_num_by_date():
    # 获取当前时间和10天前的时间
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)

    # 生成日期序列
    date_series = generate_date_series(start_date, end_date)

    # 查询数据库中过去10天每天的图片数量
    image_counts_by_date = db.session.query(
        func.strftime('%Y-%m-%d', Image.img_date).label('date'),
        func.count(Image.id).label('count')
    ).filter(
        and_(Image.img_date >= start_date, Image.img_date <= end_date)
    ).group_by(
        func.strftime('%Y-%m-%d', Image.img_date)
    ).order_by(
        'date'
    ).all()

    # 将查询结果转换为字典以便后续处理
    image_count_dict = {item.date: item.count for item in image_counts_by_date}

    # 合并结果，确保所有日期都存在，并且对于没有数据的日子填充0
    image_count_list = [{'date': date, 'count': image_count_dict.get(date, 0)} for date in date_series]

    return image_count_list

def get_tag_frequencies():
    # 使用左外连接以确保所有标签都被包括进来，即使它们没有关联的图片
    tag_frequencies = db.session.query(
        Tag.id,
        Tag.name,
        func.coalesce(func.count(ImageTag.tag_id), 0).label('frequency')  # 使用 coalesce 将 NULL 替换为 0
    ).outerjoin(
        ImageTag, Tag.id == ImageTag.tag_id  # 使用左外连接
    ).group_by(
        Tag.id, Tag.name  # 按标签ID和名称分组
    ).order_by(
        func.coalesce(func.count(ImageTag.tag_id), 0).desc()  # 按频率降序排列
    ).all()

    # 将结果整理成一个易于阅读的列表格式
    frequency_list = [{'id': tag_id, 'name': name, 'frequency': freq} for tag_id, name, freq in tag_frequencies]

    return frequency_list

def get_unlabeled_image_percentage():
    # 查询所有图片的总数
    total_images = db.session.query(func.count(Image.id)).scalar()

    if total_images == 0:
        return "No images available."

    # 查询未标记图片的数量
    unlabeled_images = db.session.query(func.count(Image.id)).filter(Image.is_labeled == False).scalar()

    # 计算未标记图片的比例
    percentage = (unlabeled_images / total_images) * 100

    return percentage, total_images
