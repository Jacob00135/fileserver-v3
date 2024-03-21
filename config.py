import os
import sqlite3
from werkzeug.security import generate_password_hash
from flask import Flask, current_app, g
from utils import get_all_disk_path

root_path = os.path.dirname(os.path.realpath(__file__))
database_path = os.path.join(root_path, 'database_sqlite')
if not os.path.exists(database_path):
    os.mkdir(database_path)

disk_path_list = list(get_all_disk_path())


class Config(object):
    # Flask app初始化时所必须的密钥
    SECRET_KEY = os.urandom(16)

    # 管理员用户名
    FLASK_ADMIN_USERNAME = 'admin'

    # 密码允许使用的字符
    PASSWORD_ALLOW_CHAR = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_',
        '=', '+', '[', '{', ']', '}', '|', ';', ':', "'", '"', ',', '.',
        '<', '>', '?'
    ]


class DevelopmentConfig(Config):
    DATABASE_PATH = os.path.join(database_path, 'db_development.sqlite')
    FLASK_ADMIN_PASSWORD = os.environ.get('FLASK_ADMIN_PASSWORD')


class ProductionConfig(Config):
    DATABASE_PATH = os.path.join(database_path, 'db.sqlite')
    FLASK_ADMIN_PASSWORD = os.environ.get('FLASK_ADMIN_PASSWORD')


class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = os.path.join(database_path, 'db_test.sqlite')
    FLASK_ADMIN_PASSWORD = '123456'


class Permission(object):
    anonymous = 1
    admin = 4


def init_database(config_obj):
    # 连接数据库，同时也能在数据库不存在时创建数据库
    con = sqlite3.connect(config_obj.DATABASE_PATH)
    cursor = con.cursor()
    
    # 建表：users
    create_users_table_sql = """
        CREATE TABLE IF NOT EXISTS `users`(
            `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `user_name` VARCHAR(255) NOT NULL UNIQUE,
            `user_password_hash` VARCHAR(255) NOT NULL
        );
    """
    cursor.execute(create_users_table_sql)
    con.commit()

    # 查询管理员记录
    result = cursor.execute(
        'SELECT COUNT(*) FROM `users` WHERE user_name=?;',
        (config_obj.FLASK_ADMIN_USERNAME, )
    ).fetchone()

    # 如果没有管理员记录，则插入管理员记录
    if result[0] <= 0:
        admin_password_hash = generate_password_hash(config_obj.FLASK_ADMIN_PASSWORD)
        cursor.execute(
            'INSERT INTO `users`(`user_name`, `user_password_hash`) VALUES(?, ?);',
            (config_obj.FLASK_ADMIN_USERNAME, admin_password_hash)
        )
        con.commit()

    # 建表：visible_dir
    create_visible_dir_table_sql = """
        CREATE TABLE IF NOT EXISTS `visible_dir`(
            `dir_id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `dir_path` TEXT NOT NULL UNIQUE,
            `dir_permission` INTEGER NOT NULL
        );
    """
    cursor.execute(create_visible_dir_table_sql)
    con.commit()

    # 将所有盘的根目录写入数据库，权限为仅管理员可访问
    for disk_path in disk_path_list:
        result = cursor.execute(
            'SELECT COUNT(*) FROM `visible_dir` WHERE `dir_path`=?;',
            (disk_path, )
        ).fetchone()
        if result[0] > 0:
            continue

        cursor.execute(
            'INSERT INTO `visible_dir`(`dir_path`, `dir_permission`) VALUES(?, ?);',
            (disk_path, Permission.admin)
        )
        con.commit()

    # 关闭连接
    cursor.close()
    con.close()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(exception_message=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def create_app(config_name):
    # 选择环境
    app = Flask(__name__)
    config_obj = config_mapping[config_name]
    app.config.from_object(config_obj)

    # 初始化数据库
    init_database(config_obj)

    # 让每一次请求结束后，关闭与数据库的连接
    app.teardown_appcontext(close_db)

    # 注册蓝图
    from main_views import main_blueprint
    from auth_views import auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app


config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}


if __name__ == '__main__':
    init_database(TestConfig)
