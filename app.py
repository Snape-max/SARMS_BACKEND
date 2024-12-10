from flask import Flask
from model import db
from view import account_bp, file_bp
from config import config
from flask_cors import CORS
from flask_migrate import Migrate
from model import initialize_tags



def create_app():
    app = Flask(__name__, static_folder='front', static_url_path='')
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(config["default"])
    # 在扩展类实例化前加载配置
    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(account_bp)
    app.register_blueprint(file_bp)
    with app.app_context():
        initialize_tags()
    return app










