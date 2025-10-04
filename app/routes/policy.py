from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import SecurityPolicy, PolicyAcknowledgement, User
from app import db

bp = Blueprint('policy', __name__, url_prefix='/policies')

@bp.route('/')
@login_required
def policy_list():
    policies = SecurityPolicy.query.order_by(SecurityPolicy.upload_date.desc()).all()
    # For current user, which have been acknowledged
    acknowledged = {a.policy_id for a in PolicyAcknowledgement.query.filter_by(user_id=current_user.id)}
    return render_template('policy/list.html', policies=policies, acknowledged=acknowledged)

@bp.route('/<int:policy_id>/', methods=['GET', 'POST'])
@login_required
def policy_view(policy_id):
    policy = SecurityPolicy.query.get_or_404(policy_id)
    acknowledged = PolicyAcknowledgement.query.filter_by(user_id=current_user.id, policy_id=policy_id).first()
    if request.method == 'POST' and not acknowledged:
        ack = PolicyAcknowledgement(user_id=current_user.id, policy_id=policy_id)
        db.session.add(ack)
        db.session.commit()
        flash('Policy acknowledged!')
        return redirect(url_for('policy.policy_list'))
    return render_template('policy/view.html', policy=policy, acknowledged=bool(acknowledged))

@bp.route('/acknowledgements/')
@login_required
def acknowledgements():
    # Admin view: list of all users & which policies they've acknowledged
    policies = SecurityPolicy.query.all()
    users = User.query.all()
    acks = PolicyAcknowledgement.query.all()
    ack_map = {(a.user_id, a.policy_id): a.acknowledged_at for a in acks}
    return render_template('policy/acknowledgements.html', policies=policies, users=users, ack_map=ack_map)