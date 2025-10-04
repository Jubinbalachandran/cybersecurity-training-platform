"""
Authentication-related routes (login, logout, registration).
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db, login_manager

bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin.dashboard') if user.role == 'admin' else url_for('superadmin.dashboard'))
        flash('Invalid credentials')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow first user to be superadmin, then restrict registration
    if User.query.first():
        flash('Registration is closed. Please contact the superadmin.')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('auth.register'))
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='superadmin'
        )
        db.session.add(user)
        db.session.commit()
        flash('Superadmin account created. Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')