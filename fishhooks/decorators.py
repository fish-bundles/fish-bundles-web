from functools import wraps

from flask import g, redirect


def authenticated(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = g.user
        if not user:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated
