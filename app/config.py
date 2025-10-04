"""
Configuration for Flask app.
Edit SECRET_KEY and SQLALCHEMY_DATABASE_URI as needed.
"""

import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "replace-this-with-a-secure-key")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cybersec_training.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # ...existing config... for mailserver
    MAIL_SERVER = 'smtp.yourprovider.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your@email.com'
    MAIL_PASSWORD = 'yourpassword'
    MAIL_DEFAULT_SENDER = 'your@email.com'