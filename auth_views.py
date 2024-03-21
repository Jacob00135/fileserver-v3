from werkzeug.security import check_password_hash
from flask import (
    Blueprint, request, session, url_for, render_template, flash,
    redirect, abort
)
from config import get_db

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # 不允许已经登录的用户访问
    if session.get('user_id') is not None:
        abort(403)

    # GET请求
    if request.method == 'GET':
        return render_template('login.html')
    
    db = get_db()

    # 检查用户名
    user_name = request.form.get('username', '', type=str)
    user = db.execute(
        'SELECT * FROM `users` WHERE `user_name`=?;',
        (user_name, )
    ).fetchone()
    if user is None:
        flash('用户名不存在')
        return redirect(url_for('auth.login'))

    # 检查密码
    password = request.form.get('password', '', type=str)
    if not check_password_hash(user['user_password_hash'], password):
        flash('密码错误')
        return redirect(url_for('auth.login'))

    # 登录
    session['user_id'] = user['user_id']

    return redirect(url_for('main.index'))
