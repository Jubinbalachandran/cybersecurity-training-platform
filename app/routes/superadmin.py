"""
Super Admin dashboard and superadmin-only features.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'superadmin':
        return "Access denied", 403
    return render_template('superadmin/dashboard.html')