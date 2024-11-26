import os.path
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file
from model import User, db, Image
from functools import wraps
import jwt
from utils import allowed_file
from config import _SECRET_KEY

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
                'exp': datetime.utcnow() + timedelta(minutes=30)
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
        image = Image(img_path=f"file/{file.filename}", img_date=datetime.now(), img_name=file.filename,
                       author_id=user.id)
        db.session.add(image)
        db.session.commit()
        filename = file.filename
        file.save(f"uploads/{filename}")
        return jsonify({'message': f'File {filename} has been uploaded successfully.'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400


@file_bp.route('/file/<filename>')
@token_required
def get_file(current_user, filename):
    if os.path.exists(f"uploads/{filename}"):
        return send_file(f"uploads/{filename}")
    else:
        return jsonify({'error': 'File not found'}), 404


