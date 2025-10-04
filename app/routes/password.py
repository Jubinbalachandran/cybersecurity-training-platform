import re
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

bp = Blueprint('password', __name__, url_prefix='/password')

@bp.route('/best-practices')
@login_required
def best_practices():
    return render_template('password/best_practices.html')

@bp.route('/check', methods=['GET', 'POST'])
@login_required
def password_check():

@bp.route('/check', methods=['GET', 'POST'])
@login_required
def password_check():
    if request.method == 'POST':
        pwd = request.form['password']
        score = 0
        feedback = []
        if len(pwd) >= 12:
            score += 2
        else:
            feedback.append("Use at least 12 characters.")
        if re.search(r'[A-Z]', pwd):
            score += 1
        else:
            feedback.append("Add an uppercase letter.")
        if re.search(r'[a-z]', pwd):
            score += 1
        else:
            feedback.append("Add a lowercase letter.")
        if re.search(r'[0-9]', pwd):
            score += 1
        else:
            feedback.append("Add a number.")
        if re.search(r'[\W_]', pwd):
            score += 1
        else:
            feedback.append("Add a symbol (e.g., !@#$).")
        levels = ['Weak', 'Fair', 'Strong', 'Very Strong', 'Excellent']
        return jsonify({
            'score': score,
            'strength': levels[min(score, 4)],
            'feedback': feedback
        })
    return render_template('password/check.html')