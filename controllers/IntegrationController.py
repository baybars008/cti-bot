# Integration Controller - Hafta 6 Third-party Entegrasyonlar
# Slack, Email, Teams entegrasyonları için controller

from flask import render_template, jsonify, request
from utils.integration_manager import integration_manager
from utils.slack_integration import slack_integration
from utils.email_integration import email_integration
from utils.teams_integration import teams_integration
from datetime import datetime, timedelta

def controller_test_integrations():
    """Tüm entegrasyonları test et"""
    try:
        results = integration_manager.test_all_integrations()
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_integration_status():
    """Entegrasyon durumlarını al"""
    try:
        status = integration_manager.get_integration_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_send_attack_alert():
    """Saldırı uyarısı gönder"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON verisi gerekli'
            }), 400
        
        platforms = data.get('platforms', ['slack', 'email', 'teams'])
        
        results = integration_manager.send_attack_alert(data, platforms)
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_send_daily_summary():
    """Günlük özet gönder"""
    try:
        platforms = request.args.get('platforms', 'email').split(',')
        
        results = integration_manager.send_daily_summary(platforms)
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_send_weekly_report():
    """Haftalık rapor gönder"""
    try:
        platforms = request.args.get('platforms', 'slack,email,teams').split(',')
        
        results = integration_manager.send_weekly_report(platforms)
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_send_system_alert():
    """Sistem uyarısı gönder"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON verisi gerekli'
            }), 400
        
        alert_type = data.get('alert_type', 'System')
        message = data.get('message', 'Test mesajı')
        severity = data.get('severity', 'info')
        platforms = data.get('platforms', ['slack', 'teams'])
        
        results = integration_manager.send_system_alert(alert_type, message, severity, platforms)
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_slack_test():
    """Slack bağlantısını test et"""
    try:
        result = slack_integration.test_connection()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_email_test():
    """Email bağlantısını test et"""
    try:
        result = email_integration.test_connection()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_teams_test():
    """Teams bağlantısını test et"""
    try:
        result = teams_integration.test_connection()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_send_custom_message():
    """Özel mesaj gönder"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON verisi gerekli'
            }), 400
        
        platform = data.get('platform', 'slack')
        title = data.get('title', 'CTI-BOT Bildirimi')
        message = data.get('message', 'Test mesajı')
        
        results = {}
        
        if platform == 'slack':
            success = slack_integration.send_custom_message(title, message)
            results['slack'] = {'success': success}
        elif platform == 'email':
            recipients = data.get('recipients', [])
            if not recipients:
                return jsonify({
                    'success': False,
                    'error': 'Email alıcıları gerekli'
                }), 400
            
            success = email_integration.send_email(recipients, title, message)
            results['email'] = {'success': success}
        elif platform == 'teams':
            success = teams_integration.send_message(message, title)
            results['teams'] = {'success': success}
        else:
            return jsonify({
                'success': False,
                'error': 'Desteklenmeyen platform'
            }), 400
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_integration_config():
    """Entegrasyon konfigürasyonunu al"""
    try:
        config = {
            'slack': {
                'webhook_url': 'SLACK_WEBHOOK_URL' if slack_integration.webhook_url else None,
                'channel': slack_integration.channel,
                'username': slack_integration.username,
                'enabled': slack_integration.enabled
            },
            'email': {
                'smtp_server': email_integration.smtp_server,
                'smtp_port': email_integration.smtp_port,
                'sender_email': email_integration.sender_email,
                'sender_name': email_integration.sender_name,
                'enabled': email_integration.enabled
            },
            'teams': {
                'webhook_url': 'TEAMS_WEBHOOK_URL' if teams_integration.webhook_url else None,
                'enabled': teams_integration.enabled
            }
        }
        
        return jsonify({
            'success': True,
            'data': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

