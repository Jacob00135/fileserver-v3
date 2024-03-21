from flask import current_app
from config import get_db


def get_admin():
    db = get_db()
    admin = db.execute(
        'SELECT * FROM `users` WHERE `user_name`=?;',
        (current_app.config['FLASK_ADMIN_USERNAME'], )
    ).fetchone()

    return admin
