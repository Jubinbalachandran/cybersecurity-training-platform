"""
Training module management, user training, and progress tracking routes.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import TrainingModule, UserProgress
from app import db

bp = Blueprint('training', __name__, url_prefix='/training')

@bp.route('/')
@login_required
def index():
    modules = TrainingModule.query.all()
    # Get user's completed modules
    completed = {up.module_id for up in UserProgress.query.filter_by(user_id=current_user.id, completed=True).all()}
    return render_template('training/index.html', modules=modules, completed=completed)

@bp.route('/view/<int:module_id>')
@login_required
def view(module_id):
    module = TrainingModule.query.get_or_404(module_id)
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module_id).first()
    is_completed = progress.completed if progress else False
    return render_template('training/view.html', module=module, is_completed=is_completed)

@bp.route('/complete/<int:module_id>', methods=['POST'])
@login_required
def complete(module_id):
    module = TrainingModule.query.get_or_404(module_id)
    progress = UserProgress.query.filter_by(user_id=current_user.id, module_id=module_id).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, module_id=module_id, completed=True)
        db.session.add(progress)
    else:
        progress.completed = True
    db.session.commit()
    flash('Module marked as completed.')
    return redirect(url_for('training.view', module_id=module_id))