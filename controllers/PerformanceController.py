# Performance Controller - Hafta 6 Performance Optimizasyonu
# Cache ve database optimizasyonu için controller

from models.DBModel import *
from flask import render_template, jsonify, request
from utils.cache_manager import cache_manager, CacheKeys
from utils.database_optimizer import db_optimizer
from datetime import datetime, timedelta

def controller_cache_stats():
    """Cache istatistiklerini döndür"""
    try:
        stats = cache_manager.get_cache_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_clear_cache():
    """Cache'i temizle"""
    try:
        cache_type = request.args.get('type', 'all')
        
        if cache_type == 'dashboard':
            cache_manager.invalidate_dashboard_cache()
            message = "Dashboard cache temizlendi"
        elif cache_type == 'export':
            cache_manager.invalidate_export_cache()
            message = "Export cache temizlendi"
        elif cache_type == 'all':
            cache_manager.invalidate_dashboard_cache()
            cache_manager.invalidate_export_cache()
            message = "Tüm cache temizlendi"
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz cache türü'
            }), 400
        
        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_database_stats():
    """Database istatistiklerini döndür"""
    try:
        stats = db_optimizer.get_table_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_optimize_database():
    """Database optimizasyonu yap"""
    try:
        # İndeksleri oluştur
        index_result = db_optimizer.create_indexes()
        
        # Database'i temizle
        vacuum_result = db_optimizer.vacuum_database()
        
        # Performans testlerini çalıştır
        performance_tests = db_optimizer.run_performance_tests()
        
        return jsonify({
            'success': True,
            'data': {
                'indexes_created': index_result,
                'database_vacuumed': vacuum_result,
                'performance_tests': performance_tests
            },
            'message': 'Database optimizasyonu tamamlandı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_performance_monitor():
    """Performans izleme verilerini döndür"""
    try:
        # Cache istatistikleri
        cache_stats = cache_manager.get_cache_stats()
        
        # Database istatistikleri
        db_stats = db_optimizer.get_table_statistics()
        
        # İndeks kullanım istatistikleri
        index_stats = db_optimizer.get_index_usage_stats()
        
        # Performans testleri
        performance_tests = db_optimizer.run_performance_tests()
        
        data = {
            'cache': cache_stats,
            'database': db_stats,
            'indexes': index_stats,
            'performance_tests': performance_tests,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_query_analyzer():
    """Query analizi yap"""
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parametresi gerekli'
            }), 400
        
        # Query performansını analiz et
        result = db_optimizer.analyze_query_performance(query)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_auto_optimize():
    """Otomatik optimizasyon yap"""
    try:
        results = {}
        
        # 1. Database indekslerini oluştur
        results['indexes'] = db_optimizer.create_indexes()
        
        # 2. Database'i temizle
        results['vacuum'] = db_optimizer.vacuum_database()
        
        # 3. Cache'i temizle
        cache_manager.invalidate_dashboard_cache()
        cache_manager.invalidate_export_cache()
        results['cache_cleared'] = True
        
        # 4. Performans testlerini çalıştır
        results['performance_tests'] = db_optimizer.run_performance_tests()
        
        return jsonify({
            'success': True,
            'data': results,
            'message': 'Otomatik optimizasyon tamamlandı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

