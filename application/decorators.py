from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role:
                flash('Accès interdit. Vous n\'avez pas les permissions nécessaires.')
                return redirect(url_for('index'))  
            return f(*args, **kwargs)
        return decorated_function
    return decorator
