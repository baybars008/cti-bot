# Monitoring Controller - Hafta 7 Monitoring ve Optimizasyon
# Error tracking, performance monitoring ve ML model yönetimi

from flask import render_template, jsonify, request
from utils.monitoring_system import monitoring_system
from utils.advanced_analytics import advanced_analytics
from utils.ml_models import ml_models
from datetime import datetime, timedelta

def controller_monitoring_dashboard():
    """Monitoring dashboard sayfası"""
    return render_template('monitoring_dashboard.html')

def controller_performance_summary():
    """Performans özetini al"""
    try:
        summary = monitoring_system.get_performance_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_error_summary():
    """Hata özetini al"""
    try:
        summary = monitoring_system.get_error_summary()
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_system_health():
    """Sistem sağlık durumunu al"""
    try:
        health = monitoring_system.get_system_health()
        return jsonify({
            'success': True,
            'data': health
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_clear_metrics():
    """Metrikleri temizle"""
    try:
        monitoring_system.clear_metrics()
        return jsonify({
            'success': True,
            'message': 'Metrics cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_attack_patterns():
    """Saldırı pattern'lerini analiz et"""
    try:
        days = int(request.args.get('days', 30))
        patterns = advanced_analytics.generate_attack_patterns(days)
        
        return jsonify({
            'success': True,
            'data': patterns
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_detect_anomalies():
    """Anomali tespiti yap"""
    try:
        days = int(request.args.get('days', 30))
        anomalies = advanced_analytics.detect_anomalies(days)
        
        return jsonify({
            'success': True,
            'data': anomalies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_generate_predictions():
    """Gelecek tahminleri oluştur"""
    try:
        days = int(request.args.get('days', 30))
        predictions = advanced_analytics.generate_predictions(days)
        
        return jsonify({
            'success': True,
            'data': predictions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_generate_insights():
    """Akıllı öngörüler oluştur"""
    try:
        days = int(request.args.get('days', 30))
        insights = advanced_analytics.generate_insights(days)
        
        return jsonify({
            'success': True,
            'data': insights
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_train_risk_classifier():
    """Risk sınıflandırıcısı eğit"""
    try:
        days = int(request.args.get('days', 90))
        result = ml_models.train_risk_classifier(days)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_train_threat_classifier():
    """Tehdit sınıflandırıcısı eğit"""
    try:
        days = int(request.args.get('days', 90))
        result = ml_models.train_threat_classifier(days)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_train_sector_classifier():
    """Sektör sınıflandırıcısı eğit"""
    try:
        days = int(request.args.get('days', 90))
        result = ml_models.train_sector_classifier(days)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_predict_risk_level():
    """Risk seviyesi tahmin et"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON verisi gerekli'
            }), 400
        
        prediction = ml_models.predict_risk_level(
            sector=data.get('sector', 'Unknown'),
            country=data.get('country', 'Unknown'),
            threat_actor=data.get('threat_actor', 'Unknown'),
            hour=data.get('hour', 12),
            weekday=data.get('weekday', 0),
            month=data.get('month', 1),
            data_type_leaked=data.get('data_type_leaked', 'Unknown'),
            company_size=data.get('company_size', 'Unknown')
        )
        
        return jsonify({
            'success': True,
            'data': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_predict_threat_actor():
    """Tehdit aktörü tahmin et"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON verisi gerekli'
            }), 400
        
        prediction = ml_models.predict_threat_actor(
            sector=data.get('sector', 'Unknown'),
            country=data.get('country', 'Unknown'),
            impact_level=data.get('impact_level', 'Unknown'),
            hour=data.get('hour', 12),
            weekday=data.get('weekday', 0),
            month=data.get('month', 1),
            data_type_leaked=data.get('data_type_leaked', 'Unknown'),
            company_size=data.get('company_size', 'Unknown')
        )
        
        return jsonify({
            'success': True,
            'data': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_cluster_attacks():
    """Saldırıları kümele"""
    try:
        days = int(request.args.get('days', 30))
        n_clusters = int(request.args.get('n_clusters', 5))
        result = ml_models.cluster_attacks(days, n_clusters)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_model_status():
    """Model durumunu al"""
    try:
        status = ml_models.get_model_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_ml_predictions():
    """ML tahminlerini al"""
    try:
        # Son 7 günün verilerini al
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Basit tahmin örneği
        predictions = {
            'risk_trend': 'increasing',
            'threat_level': 'high',
            'next_attack_probability': 0.75,
            'recommended_actions': [
                'Increase security monitoring',
                'Update threat intelligence',
                'Review access controls'
            ],
            'confidence_score': 0.82,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': predictions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

