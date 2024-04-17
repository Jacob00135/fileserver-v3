import os
from flask import current_app
from config import get_db


def get_admin():
    db = get_db()
    admin = db.execute(
        'SELECT * FROM `users` WHERE `user_name`=?;',
        (current_app.config['FLASK_ADMIN_USERNAME'], )
    ).fetchone()

    return admin


def check_visible_dir_exists():
    db = get_db()

    # 检查所有可见目录是否存在，若不存在则删除
    records = db.execute(
        'SELECT `dir_id`, `dir_path` FROM `visible_dir`;'
    ).fetchall()
    delete_id_list = []
    for r in records:
        if not os.path.exists(r['dir_path']):
            delete_id_list.append((r['dir_id'], ))
    db.executemany(
        'DELETE FROM `visible_dir` WHERE `dir_id`=?;',
        delete_id_list
    )
