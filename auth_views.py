from functools import wraps
from werkzeug.security import check_password_hash
from flask import (
    Blueprint, request, session, url_for, render_template, flash,
    redirect, abort
)
from config import get_db, Permission

auth_blueprint = Blueprint('auth', __name__)


def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorator


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # 不允许已经登录的用户访问
    if session.get('user_id') is not None:
        return redirect(url_for('main.index'))

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


@auth_blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))


@auth_blueprint.route('/manage')
@login_required
def manage_visible_dir():
    db = get_db()
    vd_list = db.execute(
        'SELECT * FROM `visible_dir` ORDER BY `dir_permission`;'
    ).fetchall()
    return render_template(
        'manage_visible_dir.html',
        vd_list=vd_list,
        permission_mapping=Permission.permission_mapping
    )


@auth_blueprint.route('/delete_visible_dir/<int:dir_id>')
@login_required
def delete_visible_dir(dir_id):
    db = get_db()
    db.execute(
        'DELETE FROM `visible_dir` WHERE `dir_id`=?;',
        (dir_id, )
    )
    db.commit()
    return redirect(url_for('auth.manage_visible_dir'))
