from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import PhishingTemplate, PhishingCampaign, PhishingTarget, User
from app import db
from flask import send_file
import io
from datetime import datetime


bp = Blueprint('phishing', __name__, url_prefix='/phishing')

# --- Template Management (continued) ---

@bp.route('/templates/edit/<int:template_id>', methods=['GET', 'POST'])
@login_required
def templates_edit(template_id):
    template = PhishingTemplate.query.get_or_404(template_id)
    if request.method == 'POST':
        template.name = request.form['name']
        template.subject = request.form['subject']
        template.body_html = request.form['body_html']
        template.body_text = request.form['body_text']
        db.session.commit()
        flash('Template updated.')
        return redirect(url_for('phishing.templates_list'))
    return render_template('phishing/templates_edit.html', template=template)

@bp.route('/templates/delete/<int:template_id>', methods=['POST'])
@login_required
def templates_delete(template_id):
    template = PhishingTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash('Template deleted.')
    return redirect(url_for('phishing.templates_list'))

# --- Campaign Management ---

@bp.route('/campaigns/')
@login_required
def campaigns_list():
    campaigns = PhishingCampaign.query.order_by(PhishingCampaign.launch_time.desc()).all()
    return render_template('phishing/campaigns_list.html', campaigns=campaigns)

@bp.route('/campaigns/add', methods=['GET', 'POST'])
@login_required
def campaigns_add():
    templates = PhishingTemplate.query.all()
    users = User.query.all()
    if request.method == 'POST':
        name = request.form['name']
        template_id = int(request.form['template_id'])
        selected_user_ids = request.form.getlist('user_ids')
        launch_time = datetime.strptime(request.form['launch_time'], "%Y-%m-%dT%H:%M")
        campaign = PhishingCampaign(name=name, template_id=template_id, launch_time=launch_time)
        db.session.add(campaign)
        db.session.commit()
        for user_id in selected_user_ids:
            target = PhishingTarget(campaign_id=campaign.id, user_id=int(user_id))
            db.session.add(target)
        db.session.commit()
        flash('Phishing campaign created.')
        return redirect(url_for('phishing.campaigns_list'))
    return render_template('phishing/campaigns_add.html', templates=templates, users=users)

@bp.route('/campaigns/<int:campaign_id>/launch', methods=['POST'])
@login_required
def campaign_launch(campaign_id):
    campaign = PhishingCampaign.query.get_or_404(campaign_id)
    targets = PhishingTarget.query.filter_by(campaign_id=campaign_id).all()
    template = PhishingTemplate.query.get(campaign.template_id)
    for target in targets:
        if not target.tracking_key:
            # generate if not present (if using migration)
            import uuid
            target.tracking_key = str(uuid.uuid4())
        send_phishing_email(target, template)
        target.email_sent = datetime.utcnow()
    campaign.launched = True
    db.session.commit()
    flash('Phishing campaign launched and emails sent.')
    return redirect(url_for('phishing.campaigns_list'))

# --- Campaign Results ---

@bp.route('/campaigns/<int:campaign_id>/results')
@login_required
def campaign_results(campaign_id):
    campaign = PhishingCampaign.query.get_or_404(campaign_id)
    targets = PhishingTarget.query.filter_by(campaign_id=campaign_id).all()
    users = {u.id: u for u in User.query.all()}
    return render_template('phishing/campaigns_results.html', campaign=campaign, targets=targets, users=users)

# Assuming you have all PhishingTarget entries for all campaigns

from collections import Counter

all_targets = PhishingTarget.query.all()
offender_counts = Counter()

for t in all_targets:
    if t.link_clicked or t.data_submitted:
        offender_counts[t.user_id] += 1

REPEAT_THRESHOLD = 2  # Set your threshold for "repeat"
repeat_offenders = {user_id for user_id, count in offender_counts.items() if count >= REPEAT_THRESHOLD}

# You would then continue with endpoints for sending emails, tracking, and a landing page.

@bp.route('/phish/<key>', methods=['GET', 'POST'])
def landing(key):
    target = PhishingTarget.query.filter_by(tracking_key=key).first_or_404()
    # Log the click if not already logged
    if not target.link_clicked:
        target.link_clicked = datetime.utcnow()
        db.session.commit()
    # Render a generic "login" page or data entry form (for realism)
    if request.method == 'POST':
        target.data_submitted = datetime.utcnow()
        db.session.commit()
        return render_template('phishing/thank_you.html')
    return render_template('phishing/landing.html', target=target)

@bp.route('/phish/pixel/<key>.gif')
def pixel(key):
    target = PhishingTarget.query.filter_by(tracking_key=key).first()
    if target and not target.email_opened:
        target.email_opened = datetime.utcnow()
        db.session.commit()
    # 1x1 transparent GIF
    gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF!\xF9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return send_file(io.BytesIO(gif_bytes), mimetype='image/gif')

@bp.route('/phish/<key>', methods=['GET', 'POST'])
def landing(key):
    target = PhishingTarget.query.filter_by(tracking_key=key).first_or_404()
    from datetime import datetime
    # Log click
    if not target.link_clicked:
        target.link_clicked = datetime.utcnow()
        db.session.commit()
    # Handle "Report as Phish"
    if request.method == 'POST' and request.form.get('report_phish') == 'yes':
        target.reported_phish = datetime.utcnow()
        db.session.commit()
        return render_template('phishing/thank_you.html', message="Thank you for reporting this email as phishing. You made the right choice!")
    # Handle fake form submission
    if request.method == 'POST':
        target.data_submitted = datetime.utcnow()
        db.session.commit()
        return render_template('phishing/thank_you.html', message="Thank you for your response.")
    return render_template('phishing/landing.html', target=target)

def assign_remediation(user_id, reason):
    already_assigned = RemediationAssignment.query.filter_by(user_id=user_id, completed=False).first()
    if not already_assigned:
        remediation = RemediationAssignment(user_id=user_id, reason=reason)
        db.session.add(remediation)
        db.session.commit()

# In your click or submit handling logic:
if not target.link_clicked:
    target.link_clicked = datetime.utcnow()
    assign_remediation(target.user_id, "Clicked phishing link")
    db.session.commit()
if request.method == 'POST' and not target.data_submitted:
    target.data_submitted = datetime.utcnow()
    assign_remediation(target.user_id, "Submitted data to phishing form")
    db.session.commit()

user_risk = {}
for user in users.values():
    targets = [t for t in all_targets if t.user_id == user.id]
    score = 0
    for t in targets:
        if t.email_opened: score += 1
        if t.link_clicked: score += 3
        if t.data_submitted: score += 5
        if t.reported_phish: score -= 4
    user_risk[user.id] = score

# Optionally, define risk levels:
def risk_level(score):
    if score >= 8:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"

import csv
from flask import Response

@bp.route('/campaigns/<int:campaign_id>/export/csv')
@login_required
def campaign_export_csv(campaign_id):
    campaign = PhishingCampaign.query.get_or_404(campaign_id)
    targets = PhishingTarget.query.filter_by(campaign_id=campaign_id).all()
    users = {u.id: u for u in User.query.all()}

    def generate():
        data = csv.writer()
        data.writerow(["User", "Email Sent", "Email Opened", "Link Clicked", "Data Submitted", "Reported as Phish"])
        for t in targets:
            data.writerow([
                users[t.user_id].username,
                t.email_sent, t.email_opened, t.link_clicked, t.data_submitted, t.reported_phish
            ])
        yield data.getvalue()

    headers = {
        "Content-Disposition": f"attachment; filename=campaign_{campaign_id}_results.csv"
    }
    return Response(generate(), mimetype='text/csv', headers=headers)	

@bp.route('/dashboard')
@login_required
def dashboard():
    from collections import Counter
    from app.models import PhishingTarget, User

    all_targets = PhishingTarget.query.all()
    users = {u.id: u for u in User.query.all()}

    # Aggregate counts
    total_targets = len(all_targets)
    opened = sum(1 for t in all_targets if t.email_opened)
    clicked = sum(1 for t in all_targets if t.link_clicked)
    submitted = sum(1 for t in all_targets if t.data_submitted)
    reported = sum(1 for t in all_targets if t.reported_phish)

    # Repeat offenders
    offender_counts = Counter()
    for t in all_targets:
        if t.link_clicked or t.data_submitted:
            offender_counts[t.user_id] += 1
    REPEAT_THRESHOLD = 2
    repeat_offenders = {user_id for user_id, count in offender_counts.items() if count >= REPEAT_THRESHOLD}

    # User risk score
    user_risk = {}
    for user in users.values():
        targets = [t for t in all_targets if t.user_id == user.id]
        score = 0
        for t in targets:
            if t.email_opened: score += 1
            if t.link_clicked: score += 3
            if t.data_submitted: score += 5
            if t.reported_phish: score -= 4
        user_risk[user.id] = score

    def risk_level(score):
        if score >= 8:
            return "High"
        elif score >= 4:
            return "Medium"
        else:
            return "Low"

    return render_template(
        'phishing/dashboard.html',
        total_targets=total_targets,
        opened=opened,
        clicked=clicked,
        submitted=submitted,
        reported=reported,
        users=users,
        user_risk=user_risk,
        risk_level=risk_level,
        repeat_offenders=repeat_offenders
    )
