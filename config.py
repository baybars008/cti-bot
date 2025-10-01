"""
CTI-BOT: Advanced Cyber Threat Intelligence Platform
===================================================

Created by: Alihan Şahin | Baybars
Threat & Security Researcher

Website: https://alihansahin.com
GitHub: https://github.com/baybars008

Configuration Settings
=====================
Database and application configuration settings.
"""

import os

# Generate secret key for session management
SECRET_KEY = os.urandom(32)

# Application base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Debug mode setting
DEBUG = True

# Database connection URI
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.abspath(os.getcwd()) + "/instance/data.db"

# Disable Flask-SQLAlchemy modification tracking
SQLALCHEMY_TRACK_MODIFICATIONS = False