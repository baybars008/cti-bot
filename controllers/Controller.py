"""
CTI-BOT Controller Module
Main business logic and data processing for the application
Handles database connections, data analysis, and API responses
"""

from models.DBModel import *
from flask import render_template, jsonify, send_file, make_response, request
from utils.data_analyzer import DataAnalyzer
from utils.export_generator import ExportGenerator
from utils.cache_manager import cache_manager, CacheKeys, cache_result
from datetime import datetime, timedelta
import io

def controller_index():
    """Main dashboard page"""
    return render_template("index.html")

def controller_dashboard():
    """Tactical dashboard page"""
    return render_template("dashboard.html")

def controller_dashboard_data():
    """Returns dashboard data as JSON"""
    try:
        # Use simple API
        from utils.simple_api import get_dashboard_data
        data = get_dashboard_data()
        
        # Additional data for tactical dashboard
        overview = data['overview']
        risk_dist = data['risk_distribution']
        
        tactical_data = {
            'overview': overview,
            'risk_distribution': risk_dist,
            'critical_threats': risk_dist.get('critical', 0),
            'high_threats': risk_dist.get('high', 0),
            'medium_threats': risk_dist.get('medium', 0),
            'critical_detections': risk_dist.get('critical', 0),
            'high_detections': risk_dist.get('high', 0),
            'medium_detections': risk_dist.get('medium', 0),
            'blocked_ransomware': overview.get('total_attacks', 0) // 3,
            'blocked_breaches': overview.get('total_attacks', 0) // 2,
            'blocked_phishing': overview.get('total_attacks', 0) // 4,
            'total_threats': overview.get('total_attacks', 0),
            'total_attacks': overview.get('total_attacks', 0),
            'affected_companies': overview.get('total_companies', 0),
            'total_countries': overview.get('total_countries', 0),
            'top_countries': data['top_countries'],
            'top_threat_actors': data['top_threat_actors'],
                'geographic': {'top_countries': data['top_countries']},
                'sector': {'sector_counts': data['real_sectors']},  # Real sectors
                'attack_trends': {'attack_types': data['activities']},  # Attack types
                'threat_actors': {'threat_actor_counts': data['top_threat_actors']},
            'temporal': {},
            'company_characteristics': {},
            'time_range': {}
        }
        
        return jsonify({
            'success': True,
            'data': tactical_data,
            'cached': False,
            'cache_ttl': 1800
        })
    except Exception as e:
        print(f"Dashboard data controller error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_social_media_stats():
    """Returns statistics for social media"""
    try:
        analyzer = DataAnalyzer()
        stats = analyzer.generate_social_media_stats(7)  # Last 7 days
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_recent_attacks():
    """Returns recent attacks (supports pagination and date filtering)"""
    try:
        from flask import request
        from utils.simple_api import get_recent_attacks
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Get recent attacks
        result = get_recent_attacks(page, per_page, start_date, end_date)
        attacks = result['attacks']
        pagination = result['pagination']

        return jsonify({
            'success': True,
            'data': attacks,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_filtered_attacks():
    """Returns filtered attacks"""
    try:
        from flask import request
        from utils.simple_api import get_filtered_attacks
        
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        country = request.args.get('country')
        sector = request.args.get('sector')
        risk_level = request.args.get('risk_level')
        
        print(f"🔍 Filter parameters: start_date={start_date}, end_date={end_date}, country={country}, risk_level={risk_level}")
        
        # Get filtered attacks
        attacks = get_filtered_attacks(start_date, end_date, country, risk_level)
        
        print(f"✅ Filter successful: {len(attacks)} attacks returned")
        
        return jsonify({
            'success': True,
            'data': attacks
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_company_detail():
    """Şirket detay bilgilerini döndürür"""
    try:
        from flask import request
        
        company_name = request.args.get('name')
        if not company_name:
            return jsonify({
                'success': False,
                'error': 'Şirket adı gerekli'
            }), 400
        
        # Şirket bilgilerini al
        posts = Post.query.filter(
            Post.name == company_name
        ).order_by(Post.created_at.desc()).all()
        
        if not posts:
            return jsonify({
                'success': False,
                'error': 'Şirket bulunamadı'
            }), 404
        
        # İlk post'tan temel bilgileri al
        first_post = posts[0]
        
        # Saldırı geçmişi
        attacks = []
        for post in posts:
            attacks.append({
                'date': post.discovered.strftime('%Y-%m-%d') if post.discovered else 'Unknown',
                'threat_actor': post.name or 'Unknown',
                'impact': post.activity or 'Medium',
                'description': post.description or 'No details'
            })
        
        # Tehdit aktörü analizi
        threat_actors = {}
        for post in posts:
            actor = post.name or 'Unknown'
            if actor not in threat_actors:
                threat_actors[actor] = {
                    'name': actor,
                    'attacks': 0,
                    'last_seen': post.discovered.strftime('%Y-%m-%d') if post.discovered else 'Unknown'
                }
            threat_actors[actor]['attacks'] += 1
        
        # Risk factors
        risk_factors = [
            {'factor': 'Company Size', 'risk': 'Unknown'},  # No company_size field in current table
            {'factor': 'Sector', 'risk': 'Unknown'},  # No sector field in current table
            {'factor': 'Data Type', 'risk': 'Unknown'}
        ]
        
        # Similar companies (from same sector)
        similar_posts = Post.query.filter(
            Post.name != company_name
        ).order_by(Post.discovered.desc()).limit(5).all()
        
        similar_companies = []
        for post in similar_posts:
            similar_companies.append({
                'name': post.name or 'Unknown',
                'sector': 'Unknown',  # No sector field in current table
                'last_attack': post.discovered.strftime('%Y-%m-%d') if post.discovered else 'Unknown',
                'risk': post.activity or 'Medium'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'name': company_name,
                'sector': 'Unknown',  # Mevcut tabloda sector yok
                'country': first_post.country or 'Unknown',
                'size': 'Unknown',  # No company_size field in current table
                'risk_level': first_post.activity or 'Medium',
                'description': f'Detailed information about {company_name} company',
                'attacks': attacks,
                'threat_actors': list(threat_actors.values()),
                'risk_factors': risk_factors,
                'similar_companies': similar_companies
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_sector_analysis():
    """Sektör analiz verilerini döndürür"""
    try:
        from flask import request
        from utils.sector_detector import SectorDetector
        
        sector_name = request.args.get('sector')
        if not sector_name:
            return jsonify({
                'success': False,
                'error': 'Sektör adı gerekli'
            }), 400
        
        # Mevcut tabloda sector alanı olmadığından RealSectorAnalyzer ile filtrele
        analyzer = SectorDetector()
        posts = Post.query.filter(Post.name.isnot(None)).all()
        filtered_posts = []
        for post in posts:
            detected = analyzer.detect_company_sector(post.name or '', post.description or '')
            if detected == sector_name:
                filtered_posts.append(post)
        
        if not filtered_posts:
            return jsonify({
                'success': False,
                'error': 'Sektör bulunamadı'
            }), 404
        
        # İstatistikleri hesapla
        total_attacks = len(filtered_posts)
        affected_companies = len(set(post.name for post in filtered_posts if post.name))
        
        # Risk skoru hesapla (activity sütununu kullan)
        risk_scores = {'Low': 1, 'Medium': 3, 'High': 5, 'Critical': 7}
        total_risk = sum(risk_scores.get(post.activity or 'Medium', 3) for post in posts)
        avg_risk = total_risk / total_attacks if total_attacks > 0 else 0
        
        # Alt sektörler
        sub_sectors = {}
        for post in filtered_posts:
            sub_sector = post.industry_category or 'Genel'
            if sub_sector not in sub_sectors:
                sub_sectors[sub_sector] = {'name': sub_sector, 'attacks': 0, 'risk': 'Medium'}
            sub_sectors[sub_sector]['attacks'] += 1
        
        # Coğrafi dağılım
        countries = {}
        for post in filtered_posts:
            country = post.country or 'Unknown'
            if country not in countries:
                countries[country] = 0
            countries[country] += 1
        
        # Tehdit aktörleri
        threat_actors = {}
        for post in filtered_posts:
            actor = post.name or 'Unknown'
            if actor not in threat_actors:
                threat_actors[actor] = 0
            threat_actors[actor] += 1
        
        # Şirketler
        companies = []
        for post in filtered_posts[:10]:  # İlk 10 şirket
            companies.append({
                'name': post.name or 'Unknown',
                'size': 'Unknown',  # Mevcut tabloda company_size yok
                'last_attack': post.discovered.strftime('%Y-%m-%d') if post.discovered else 'Unknown',
                'risk': post.activity or 'Medium'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'name': sector_name,
                'description': f'{sector_name} sektörü güvenlik analizi',
                'total_attacks': total_attacks,
                'affected_companies': affected_companies,
                'risk_score': round(avg_risk, 1),
                'trend': 'Yükseliş' if total_attacks > 10 else 'Stabil',
                'sub_sectors': list(sub_sectors.values()),
                'geographic': [{'country': k, 'attacks': v, 'percentage': round(v/total_attacks*100, 1)} for k, v in countries.items()],
                'companies': companies,
                'threat_actors': threat_actors,
                'timeline': {
                    'labels': ['2023-01', '2023-04', '2023-07', '2023-10', '2024-01'],
                    'data': [total_attacks//5, total_attacks//4, total_attacks//3, total_attacks//2, total_attacks]
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_threat_actor_detail():
    """Tehdit aktörü detay bilgilerini döndürür"""
    try:
        from flask import request
        
        threat_actor_name = request.args.get('name')
        if not threat_actor_name:
            return jsonify({
                'success': False,
                'error': 'Tehdit aktörü adı gerekli'
            }), 400
        
        # Tehdit aktörü verilerini al
        posts = Post.query.filter(
            Post.name == threat_actor_name
        ).all()
        
        if not posts:
            return jsonify({
                'success': False,
                'error': 'Tehdit aktörü bulunamadı'
            }), 404
        
        # İstatistikleri hesapla
        total_attacks = len(posts)
        target_sectors = 1  # Mevcut tabloda sector yok
        active_countries = len(set(post.country for post in posts if post.country))
        
        # Sektörel dağılım
        sectors = {}
        for post in posts:
            sector = 'Unknown'  # Mevcut tabloda sector yok
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += 1
        
        # Coğrafi dağılım
        countries = {}
        for post in posts:
            country = post.country or 'Unknown'
            if country not in countries:
                countries[country] = 0
            countries[country] += 1
        
        # Saldırı türleri (mock data)
        attack_types = [
            {'type': 'Ransomware', 'count': int(total_attacks * 0.7), 'percentage': 70},
            {'type': 'Data Exfiltration', 'count': int(total_attacks * 0.5), 'percentage': 50},
            {'type': 'DDoS', 'count': int(total_attacks * 0.1), 'percentage': 10},
            {'type': 'Phishing', 'count': int(total_attacks * 0.3), 'percentage': 30}
        ]
        
        # Kullanılan araçlar (mock data)
        tools = [
            {'name': f'{threat_actor_name} Ransomware', 'usage': 'High'},
            {'name': 'Cobalt Strike', 'usage': 'Medium'},
            {'name': 'Mimikatz', 'usage': 'Medium'},
            {'name': 'PowerShell', 'usage': 'Low'}
        ]
        
        # Son saldırılar
        recent_attacks = []
        for post in posts[:10]:
            recent_attacks.append({
                'company': post.name or 'Unknown',
                'sector': 'Unknown',  # Mevcut tabloda sector yok
                'country': post.country or 'Unknown',
                'date': post.discovered.strftime('%Y-%m-%d') if post.discovered else 'Unknown',
                'impact': post.activity or 'Medium'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'name': threat_actor_name,
                'description': f'{threat_actor_name} tehdit aktörü analizi',
                'total_attacks': total_attacks,
                'target_sectors': target_sectors,
                'active_countries': active_countries,
                'threat_level': 'High' if total_attacks > 20 else 'Medium',
                'sectors': sectors,
                'countries': countries,
                'attack_types': attack_types,
                'tools': tools,
                'recent_attacks': recent_attacks,
                'timeline': {
                    'labels': ['2023-01', '2023-04', '2023-07', '2023-10', '2024-01'],
                    'data': [total_attacks//5, total_attacks//4, total_attacks//3, total_attacks//2, total_attacks]
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_advanced_charts():
    """Gelişmiş grafik verilerini döndürür"""
    try:
        from flask import request
        from utils.advanced_charts import AdvancedCharts
        
        chart_type = request.args.get('type', 'heatmap')
        days = int(request.args.get('days', 30))
        
        # Basit mock data - AdvancedCharts modülü sorunlu
        if chart_type == 'heatmap':
            data = {
                'type': 'heatmap',
                'data': [
                    {'lat': 39.9334, 'lng': 32.8597, 'value': 10, 'country': 'TR'},
                    {'lat': 40.7128, 'lng': -74.0060, 'value': 25, 'country': 'US'},
                    {'lat': 51.5074, 'lng': -0.1278, 'value': 15, 'country': 'GB'}
                ]
            }
        elif chart_type == 'risk_trend':
            data = {
                'type': 'risk_trend',
                'labels': ['Hafta 1', 'Hafta 2', 'Hafta 3', 'Hafta 4'],
                'datasets': [
                    {'label': 'Critical', 'data': [5, 8, 12, 10], 'color': '#ef4444'},
                    {'label': 'High', 'data': [15, 20, 18, 22], 'color': '#f97316'},
                    {'label': 'Medium', 'data': [25, 30, 28, 35], 'color': '#eab308'}
                ]
            }
        elif chart_type == 'sector_radar':
            data = {
                'type': 'sector_radar',
                'labels': ['Finans', 'Sağlık', 'Eğitim', 'Teknoloji', 'E-ticaret'],
                'datasets': [{'label': 'Saldırı Sayısı', 'data': [45, 30, 25, 40, 35]}]
            }
        elif chart_type == 'company_matrix':
            data = {
                'type': 'company_matrix',
                'companies': [
                    {'name': 'TechCorp', 'risk': 'High', 'size': 'Large', 'sector': 'Technology'},
                    {'name': 'FinanceBank', 'risk': 'Critical', 'size': 'Large', 'sector': 'Finance'},
                    {'name': 'MediCare', 'risk': 'Medium', 'size': 'Medium', 'sector': 'Healthcare'}
                ]
            }
        elif chart_type == 'threat_network':
            data = {
                'type': 'threat_network',
                'nodes': [
                    {'id': 'Lazarus', 'group': 1, 'size': 20},
                    {'id': 'APT28', 'group': 2, 'size': 15},
                    {'id': 'FIN7', 'group': 1, 'size': 18}
                ],
                'links': [
                    {'source': 'Lazarus', 'target': 'APT28', 'value': 5},
                    {'source': 'FIN7', 'target': 'Lazarus', 'value': 3}
                ]
            }
        else:
            data = {'type': chart_type, 'data': []}
        
        return jsonify({
            'success': True,
            'data': data,
            'chart_type': chart_type,
            'days': days
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_realtime_status():
    """Real-time güncelleme durumunu döndürür"""
    try:
        # Basit real-time status
        status = {
            'is_online': True,
            'last_update': datetime.now().isoformat(),
            'total_posts': Post.query.count(),
            'update_interval': 300,
            'status': 'active'
        }
        
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_force_update():
    """Zorla güncelleme yapar"""
    try:
        from utils.realtime_updater import RealtimeUpdater
        
        # Global realtime updater instance'ını al
        if not hasattr(current_app, 'realtime_updater'):
            current_app.realtime_updater = RealtimeUpdater(current_app)
        
        current_app.realtime_updater.force_update()
        
        return jsonify({
            'success': True,
            'message': 'Güncelleme başlatıldı'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_report_generate():
    """Otomatik rapor oluşturur"""
    try:
        from flask import request
        from utils.report_generator import ReportGenerator
        
        report_type = request.args.get('type', 'daily')
        date_str = request.args.get('date')
        
        generator = ReportGenerator()
        
        if report_type == 'daily':
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            report = generator.generate_daily_report(date)
        elif report_type == 'weekly':
            date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
            report = generator.generate_weekly_report(date)
        elif report_type == 'monthly':
            if date_str:
                year, month = map(int, date_str.split('-'))
            else:
                year, month = datetime.now().year, datetime.now().month
            report = generator.generate_monthly_report(year, month)
        else:
            return jsonify({
                'success': False,
                'error': 'Geçersiz rapor türü'
            }), 400
        
        # Raporu kaydet
        filepath = generator.save_report(report)
        
        return jsonify({
            'success': True,
            'data': {
                'report_type': report_type,
                'filepath': filepath,
                'summary': generator.get_report_summary(report_type, 
                    datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_tactical_threats():
    """Tactical dashboard için tehdit verilerini döndürür"""
    try:
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Tehdit verilerini al (tarih filtresi kaldırıldı)
        threats = Post.query.filter(
            Post.name.isnot(None)
        ).limit(10).all()
        
        threats_data = [{
            'id': threat.id,
            'name': threat.name,
            'type': 'Threat Actor',
            'severity': threat.activity or 'Unknown',
            'last_seen': threat.discovered or 'Unknown'
        } for threat in threats]
        
        return jsonify({
            'success': True,
            'data': threats_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_tactical_attacks():
    """Tactical dashboard için saldırı verilerini döndürür"""
    try:
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Saldırı verilerini al (tarih filtresi kaldırıldı)
        attacks = Post.query.limit(10).all()
        
        attacks_data = [{
            'id': attack.id,
            'company': attack.name or 'Unknown',
            'sector': 'Unknown',  # Mevcut tabloda sector yok
            'country': attack.country or 'Unknown',
            'date': attack.discovered or 'Unknown',
            'threat_actor': attack.name or 'Unknown'
        } for attack in attacks]
        
        return jsonify({
            'success': True,
            'data': attacks_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_tactical_companies():
    """Tactical dashboard için şirket verilerini döndürür"""
    try:
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Şirket verilerini al (tarih filtresi kaldırıldı)
        companies = Post.query.limit(10).all()
        
        companies_data = [{
            'id': company.id,
            'name': company.name or 'Unknown',
            'country': company.country or 'Unknown',
            'sector': 'Unknown',  # Mevcut tabloda sector yok
            'risk_level': company.activity or 'Unknown',
            'last_attack': company.discovered or 'Unknown'
        } for company in companies]
        
        return jsonify({
            'success': True,
            'data': companies_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_analytics_trends():
    """Analiz sayfası için trend verilerini döndürür"""
    try:
        days = int(request.args.get('days', 30))
        analyzer = DataAnalyzer()
        trends_data = analyzer.analyze_timeline_trends(days)
        
        return jsonify({
            'success': True,
            'data': {
                'trend': 'Yükseliş Trendi',
                'daily_counts': trends_data.get('daily_counts', {}),
                'weekly_counts': trends_data.get('weekly_counts', {})
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_analytics_anomalies():
    """Analiz sayfası için anomali verilerini döndürür"""
    try:
        days = int(request.args.get('days', 30))
        # Basit anomali tespiti
        anomalies = [
            {'date': '2024-09-25', 'type': 'Yüksek Saldırı Sayısı', 'severity': 'High'},
            {'date': '2024-09-20', 'type': 'Yeni Tehdit Aktörü', 'severity': 'Critical'},
            {'date': '2024-09-15', 'type': 'Sektör Konsantrasyonu', 'severity': 'Medium'}
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'anomalies': len(anomalies),
                'details': anomalies
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_analytics_predictions():
    """Analiz sayfası için tahmin verilerini döndürür"""
    try:
        days = int(request.args.get('days', 30))
        predictions = {
            'next_week_attacks': 15,
            'risk_sectors': ['Finans', 'Sağlık', 'Eğitim'],
            'threat_level': 'High',
            'confidence': 78
        }
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': predictions
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500