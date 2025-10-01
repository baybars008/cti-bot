"""
CTI-BOT: Advanced Cyber Threat Intelligence Platform
===================================================

Created by: Alihan Şahin | Baybars
Threat & Security Researcher

Website: https://alihansahin.com
GitHub: https://github.com/baybars008

A next-generation cyber threat intelligence platform built with
cutting-edge technology and futuristic design principles.

Mission: "To revolutionize cybersecurity through intelligent threat detection,
predictive analytics, and automated response systems that stay ahead of
evolving cyber threats."

Main application entry point
"""

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from models.DBModel import db
from routes.Route import pclist
from utils.api_generator import api_bp

# Initialize Flask application
app = Flask(__name__)
app.config.from_object('config')

# Enable CORS support
CORS(app)

# API Key configuration
app.config['API_KEY'] = 'cti-bot-api-key-2024'

# Initialize database
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(pclist)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
