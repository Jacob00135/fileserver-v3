import os
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import (
    Blueprint, request, session, url_for, render_template, flash,
    redirect, abort, current_app
)
from config import get_db, Permission
from model import check_visible_dir_exists

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


@auth_blueprint.route('modify_password', methods=['GET', 'POST'])
@login_required
def modify_password():
    if request.method == 'GET':
        return render_template('modify_password.html')

    # 检查密码长度是否合法
    password = request.form.get('password', '', type=str)
    length = len(password)
    if length < 6 or length > 16:
        flash('密码长度只能是6~16')
        return redirect(url_for('auth.modify_password'))

    # 检查密码字符是否合法
    allow_char = current_app.config['PASSWORD_ALLOW_CHAR']
    for c in password:
        if c not in allow_char:
            flash('包含不合法字符')
            return redirect(url_for('auth.modify_password'))
    
    db = get_db()

    # 修改密码
    user_id = session['user_id']
    password_hash = generate_password_hash(password)
    db.execute(
        'UPDATE `users` SET `user_password_hash`=? WHERE `user_id`=?;',
        (password_hash, user_id)
    )
    db.commit()

    return redirect(url_for('main.index'))


@auth_blueprint.route('/manage')
@login_required
def manage_visible_dir():
    check_visible_dir_exists()

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


@auth_blueprint.route('/append_visible_dir', methods=['GET', 'POST'])
@login_required
def append_visible_dir():
    if request.method == 'GET':
        return render_template(
            'append_visible_dir.html',
            permission_mapping=Permission.permission_mapping
        )

    # 检查路径是否存在磁盘中
    path = request.form.get('path', '', type=str)
    if (not os.path.exists(path)) or (not os.path.isdir(path)):
        flash('路径不存在或不是目录')
        return redirect(url_for('auth.append_visible_dir'))

    path = os.path.realpath(path)
    db = get_db()

    # 检查路径是否存在数据库中
    record = db.execute(
        'SELECT * FROM `visible_dir` WHERE `dir_path`=?;',
        (path, )
    ).fetchone()
    if record is not None:
        flash('路径已被添加过')
        return redirect(url_for('auth.append_visible_dir'))

    # 检查权限值
    permission = request.form.get('permission', 1, type=int)
    if permission not in Permission.permission_mapping:
        flash('权限值不合法')
        return redirect(url_for('auth.append_visible_dir'))

    # 添加
    db.execute(
        'INSERT INTO `visible_dir`(`dir_path`, `dir_permission`) VALUES(?, ?);',
        (path, permission)
    )
    db.commit()

    return redirect(url_for('auth.manage_visible_dir'))
