"""
SQLAlchemy models for users, roles, licensing, features, modules, and progress.
"""

from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'superadmin' or 'admin'
    is_active = db.Column(db.Boolean, default=True)

class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_limit = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    demo_only = db.Column(db.Boolean, default=False)

class TrainingModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('training_module.id'))
    completed = db.Column(db.Boolean, default=False)

class PhishingTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    subject = db.Column(db.String(200))
    body_html = db.Column(db.Text)
    body_text = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

class PhishingCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    template_id = db.Column(db.Integer, db.ForeignKey('phishing_template.id'))
    scheduled_time = db.Column(db.DateTime)
    launched = db.Column(db.Boolean, default=False)

class PhishingTarget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('phishing_campaign.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    email_sent = db.Column(db.DateTime)
    email_opened = db.Column(db.DateTime)
    link_clicked = db.Column(db.DateTime)
    data_submitted = db.Column(db.DateTime)
    reported_phish = db.Column(db.DateTime)

import uuid

class PhishingTarget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('phishing_campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email_sent = db.Column(db.DateTime)
    email_opened = db.Column(db.DateTime)
    link_clicked = db.Column(db.DateTime)
    data_submitted = db.Column(db.DateTime)
    reported_phish = db.Column(db.DateTime)
    tracking_key = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

class RemediationAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(255))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

class SecuritySurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)

class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('securitysurvey.id'), nullable=False)
    question = db.Column(db.Text)
    choices = db.Column(db.Text)  # JSON: ["Yes", "No", "Sometimes"]

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('securitysurvey.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.Text)  # JSON: {"q1": "Yes", "q2": "No"}
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
class SecuritySurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)

class SurveyQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('securitysurvey.id'), nullable=False)
    question = db.Column(db.Text)
    choices = db.Column(db.Text)  # JSON: ["Yes", "No", "Sometimes"]

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('securitysurvey.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answers = db.Column(db.Text)  # JSON: {"q1": "Yes", "q2": "No"}
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecurityPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class PolicyAcknowledgement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('securitypolicy.id'), nullable=False)
    acknowledged_at = db.Column(db.DateTime, default=datetime.utcnow)