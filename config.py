import os
import sys

_SECRET_KEY = "oxygen-x"

class Config:
    # 基本配置
    DEBUG = False
    TESTING = False

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = _SECRET_KEY
    # 动态生成数据库 URI
    WIN = sys.platform.startswith('win')
    if WIN:  # Windows 系统
        prefix = 'sqlite:///'
    else:  # 否则使用四个斜线
        prefix = 'sqlite:////'
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.db')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}