import os
from flask import (
    Blueprint, render_template, abort, session, request, send_from_directory
)
from config import Permission, get_db
from utils import MyFile, MyDir

main_blueprint = Blueprint('main', __name__)


@main_blueprint.app_errorhandler(404)
def page_not_found(e):
    status_code = 404
    response = render_template(
        'error.html',
        status_code=status_code,
        error_info='页面不存在'
    )
    return response, status_code


@main_blueprint.app_errorhandler(403)
def forbidden(e):
    status_code = 403
    response = render_template(
        'error.html',
        status_code=status_code,
        error_info='无权访问'
    )
    return response, status_code


@main_blueprint.app_errorhandler(500)
def internal_server_error(e):
    status_code = 500
    response = render_template(
        'error.html',
        status_code=status_code,
        error_info='服务器内部错误'
    )
    return response, status_code


@main_blueprint.app_errorhandler(405)
def method_not_allowed(e):
    status_code = 405
    response = render_template(
        'error.html',
        status_code=status_code,
        error_info='不允许的请求方法'
    )
    return response, status_code


@main_blueprint.route('/')
def index():
    # 获取访问权限
    if session.get('user_id') is None:
        permission = Permission.anonymous
    else:
        permission = Permission.admin

    db = get_db()

    # 获取vd参数
    vd = request.args.get('vd')
    if vd is None:
        # 显示根目录
        vd_list = db.execute(
            """
            SELECT `dir_id`, `dir_path` FROM `visible_dir`
            WHERE `dir_permission` <= ?;
            """,
            (permission, )
        ).fetchall()

        return render_template(
            'index.html',
            vd=vd,
            vd_list=vd_list
        )

    # 检查vd参数
    record = db.execute(
        'SELECT * FROM `visible_dir` WHERE `dir_path` = ?;',
        (vd, )
    ).fetchone()
    if record is None:
        abort(404)
    if record['dir_permission'] > permission:
        abort(403)

    # 获取sort_by和sort_ascending参数
    sort_by = request.args.get('sort_by', 'type')
    sort_ascending = bool(request.args.get('sort_ascending', 0, type=int))

    # 获取path参数
    path = request.args.get('path')
    if path is None:
        # 显示一个可见目录下的所有文件
        mydir = MyDir(vd)
        mydir.sort_files(by=sort_by, ascending=sort_ascending)

        return render_template(
            'index.html',
            vd=vd,
            paths=[f.filename for f in mydir.files],
            myfiles=mydir.files,
            sort_by=sort_by,
            sort_ascending=int(sort_ascending)
        )

    # 检查path参数合法性
    final_path = os.path.join(vd, path)
    if (not os.path.exists(final_path)) \
       or (not os.path.isabs(final_path)) \
       or (os.path.islink(final_path)):
        abort(404)
    final_path = os.path.realpath(final_path)

    # 访问文件时的情况
    if os.path.isfile(final_path):
        dirname, basename = os.path.split(final_path)
        return send_from_directory(
            directory=dirname,
            path=basename,
            as_attachment=False
        )

    # 如果想访问目录，则显示目录下的所有文件
    mydir = MyDir(final_path)
    mydir.sort_files(by=sort_by, ascending=sort_ascending)

    return render_template(
        'index.html',
        vd=vd,
        paths=[os.path.join(path, f.filename) for f in mydir.files],
        myfiles=mydir.files,
        sort_by=sort_by,
        sort_ascending=int(sort_ascending)
    )
