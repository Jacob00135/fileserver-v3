from functools import wraps
from flask import session, redirect, url_for


def login_required(func):
    @wraps(func)
    def decorator_func(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorator_func
