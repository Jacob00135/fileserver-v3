from flask import Blueprint, render_template, abort

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
    abort(404)
