import os.path
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from model import User, db, Image
from functools import wraps
import jwt
from utils import allowed_file
from config import _SECRET_KEY, FILE_SAVE_FOLDER, FILE_ROUTE
import hashlib
import uuid

account_bp = Blueprint('account_bp', __name__)
file_bp = Blueprint('file_bp', __name__)


@account_bp.route('/register', methods=['POST'])
def register():  # 注册接口
    if request.method == 'POST':
        data = request.json
        name = data.get('username')
        password = data.get('password')
        email = data.get('email')
        if User.query.filter(User.email == email).first() is not None:
            return jsonify(status="fail", msg="邮箱已被注册")
        user = User(name=name, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(status="success", msg="注册成功")
    return jsonify(status="fail", msg="注册失败")


@account_bp.route('/login', methods=['POST'])
def login(): # 登录接口
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        passwd = data.get('password')
        if User.query.filter(User.email == email).first() is None:
            return jsonify(status="fail", msg="邮箱未注册")
        user = User.query.filter(User.email == email).first()
        if user.check_password(passwd):
            token = jwt.encode({
                'sub': data['email'],
                'exp': datetime.utcnow() + timedelta(minutes=60)
            }, _SECRET_KEY, algorithm="HS256")
            return jsonify(status="success", msg="登录成功", token=token)
        else:
            return jsonify(status="fail", msg="密码错误")

# 登录鉴权， 用于上传，获取数据等
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, _SECRET_KEY, algorithms=["HS256"])
            current_user = data['sub']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated



@file_bp.route(f'/{FILE_ROUTE}/<filehash>')
def get_file(filehash):
    image = Image.query.filter(Image.img_md5 == filehash).first()
    if image is None:
        return jsonify({'error': 'File not found'}), 404
    return send_file(image.img_path)



@file_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    user = User.query.filter(User.email == current_user).first()
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        image = Image(img_date=datetime.now(), img_name=file.filename,
                       author_id=user.id)

        md5_hash = hashlib.md5(file.read()).hexdigest()
        _, ext = os.path.splitext(secure_filename(file.filename))
        file.seek(0)
        image.img_md5 = md5_hash
        image.img_url = f"{FILE_ROUTE}/{md5_hash}"
        image.img_path = f"{FILE_SAVE_FOLDER}/{md5_hash}{ext}"
        file.save(f"{image.img_path}")
        db.session.add(image)
        db.session.commit()
        filename = file.filename
        return jsonify({'message': f'File {filename} has been uploaded successfully.'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400



@file_bp.route('/query', methods=['GET', 'POST'])
@token_required
def query_item(current_user):
    filters = request.args
    query = Image.query
    if not filters:
        return jsonify([image.serialize() for image in query.all()])

    if 'name' in filters:
        query = query.filter(Image.img_name.like(f"%{filters['img_name']}%"))

    if 'start_date' in filters and 'end_date' in filters:
        try:
            start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Image.img_date >= start_date, Image.img_date < end_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400

    if 'id' in filters:
        try:
            image_id = uuid.UUID(filters['id'])  # 尝试将字符串转换为UUID
            query = query.filter(Image.id == image_id)
        except ValueError:
            return jsonify({'error': 'Invalid id, must be a valid UUID'}), 400

    if 'tag' in filters:
        ...

    images = query.all()
    return jsonify([image.serialize() for image in images])


@file_bp.route('/modify', methods=['POST'])
@token_required
def modify_item(current_user):
    filters = request.args
    if not filters:
        return jsonify({'error': 'No filters provided'}), 400

    if not 'id' in filters: # 需提供id
        return jsonify({'error': 'No id provided'}), 400

    # str转uuid
    image_id = None
    try:
        image_id = uuid.UUID(filters['id'])  # 尝试将字符串转换为UUID
    except ValueError:
        return jsonify({'error': 'Invalid id, must be a valid UUID'}), 400

    image = Image.query.filter(Image.id == image_id).first()
    if image is None: # 图片不存在
        return jsonify({'error': 'Image not found'}), 404

    if 'rename' in filters and filters['rename'] != '': # 重命名
        image.img_name = filters['rename']
        db.session.commit()
        return jsonify({'message': 'Image renamed successfully'}), 200
    elif 'delete' in filters and filters['delete'] == 'true': # 删除
        os.remove(image.img_path)
        image.tags.clear() # 清空标签表
        db.session.delete(image)
        db.session.commit()
        return jsonify({'message': 'Image deleted successfully'}), 200
    else:
        return jsonify({'error': 'Invalid request'}), 400



