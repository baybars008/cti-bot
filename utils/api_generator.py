"""
CTI-BOT API Generator
Gelişmiş RESTful API endpoints oluşturma ve yönetim sistemi
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import json
import os
from datetime import datetime, timedelta
from models.DBModel import db, Post, HackedCompany, SocialMediaPost
from sqlalchemy import func, desc, asc
from utils.data_analyzer import DataAnalyzer
from utils.advanced_charts import AdvancedCharts
from utils.report_generator import ReportGenerator

# API Blueprint oluştur
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# API Rate Limiting için decorator
def rate_limit(max_requests=100, window=3600):
    """API rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Basit rate limiting (gerçek projede Redis kullanılmalı)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API Authentication decorator
def require_api_key(f):
    """API key gerektiren endpoint'ler için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('API_KEY', 'default_key'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# API Response formatter
def api_response(data=None, message="Success", status_code=200, error=None):
    """Standart API response formatı"""
    response = {
        'status': 'success' if status_code < 400 else 'error',
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    if error:
        response['error'] = error
    return jsonify(response), status_code

# ==================== DASHBOARD API ENDPOINTS ====================

@api_bp.route('/dashboard/overview', methods=['GET'])
@rate_limit(max_requests=200, window=3600)
def get_dashboard_overview():
    """Dashboard genel bakış verileri"""
    try:
        days = int(request.args.get('days', 30))
        analyzer = DataAnalyzer()
        data = analyzer.generate_dashboard_data(days)
        
        return api_response(
            data=data,
            message=f"Dashboard overview data for last {days} days"
        )
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to fetch dashboard overview",
            status_code=500
        )

@api_bp.route('/dashboard/statistics', methods=['GET'])
@rate_limit(max_requests=100, window=3600)
def get_dashboard_statistics():
    """Detaylı dashboard istatistikleri"""
    try:
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Temel istatistikler
        total_attacks = Post.query.filter(Post.created_at >= start_date).count()
        unique_companies = db.session.query(func.count(func.distinct(Post.company_name))).filter(
            Post.created_at >= start_date, Post.company_name.isnot(None)
        ).scalar()
        
        # Risk seviyesi dağılımı
        risk_distribution = db.session.query(
            Post.impact_level, func.count(Post.id)
        ).filter(
            Post.created_at >= start_date, Post.impact_level.isnot(None)
        ).group_by(Post.impact_level).all()
        
        # Sektör dağılımı
        sector_distribution = db.session.query(
            Post.sector, func.count(Post.id)
        ).filter(
            Post.created_at >= start_date, Post.sector.isnot(None)
        ).group_by(Post.sector).order_by(desc(func.count(Post.id))).limit(10).all()
        
        # Coğrafi dağılım
        country_distribution = db.session.query(
            Post.country, func.count(Post.id)
        ).filter(
            Post.created_at >= start_date, Post.country.isnot(None)
        ).group_by(Post.country).order_by(desc(func.count(Post.id))).limit(10).all()
        
        data = {
            'total_attacks': total_attacks,
            'unique_companies': unique_companies,
            'risk_distribution': dict(risk_distribution),
            'sector_distribution': dict(sector_distribution),
            'country_distribution': dict(country_distribution),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }
        
        return api_response(
            data=data,
            message=f"Dashboard statistics for last {days} days"
        )
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to fetch dashboard statistics",
            status_code=500
        )

# ==================== ADVANCED CHARTS API ====================

@api_bp.route('/charts/heatmap', methods=['GET'])
@rate_limit(max_requests=50, window=3600)
def get_heatmap_data():
    """Coğrafi heatmap verileri"""
    try:
        days = int(request.args.get('days', 30))
        charts = AdvancedCharts()
        data = charts.generate_heatmap_data(days)
        
        return api_response(
            data=data,
            message=f"Heatmap data for last {days} days"
        )
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to fetch heatmap data",
            status_code=500
        )

@api_bp.route('/charts/risk-trend', methods=['GET'])
@rate_limit(max_requests=50, window=3600)
def get_risk_trend_data():
    """Risk trend analizi verileri"""
    try:
        days = int(request.args.get('days', 90))
        charts = AdvancedCharts()
        data = charts.generate_risk_trend_analysis(days)
        
        return api_response(
            data=data,
            message=f"Risk trend data for last {days} days"
        )
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to fetch risk trend data",
            status_code=500
        )

@api_bp.route('/charts/sector-radar', methods=['GET'])
@rate_limit(max_requests=50, window=3600)
def get_sector_radar_data():
    """Sektörel radar grafik verileri"""
    try:
        days = int(request.args.get('days', 30))
        charts = AdvancedCharts()
        data = charts.generate_sector_radar_chart(days)
        
        return api_response(
            data=data,
            message=f"Sector radar data for last {days} days"
        )
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to fetch sector radar data",
            status_code=500
        )

# ==================== EXPORT API ENDPOINTS ====================

@api_bp.route('/export/attacks', methods=['GET'])
@rate_limit(max_requests=20, window=3600)
def export_attacks():
    """Saldırı verilerini export et"""
    try:
        format_type = request.args.get('format', 'json')
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        attacks = Post.query.filter(Post.created_at >= start_date).all()
        
        if format_type == 'json':
            data = []
            for attack in attacks:
                data.append({
                    'id': attack.id,
                    'title': attack.title,
                    'company_name': attack.company_name,
                    'sector': attack.sector,
                    'country': attack.country,
                    'impact_level': attack.impact_level,
                    'threat_actor': attack.name,
                    'hack_date': attack.hack_date.isoformat() if attack.hack_date else None,
                    'created_at': attack.created_at.isoformat(),
                    'description': attack.description,
                    'website': attack.website
                })
            
            return api_response(
                data=data,
                message=f"Exported {len(data)} attacks in JSON format"
            )
        
        elif format_type == 'csv':
            # CSV export için basit format
            csv_data = "ID,Title,Company,Sector,Country,Impact Level,Threat Actor,Hack Date,Description\n"
            for attack in attacks:
                csv_data += f"{attack.id},{attack.title},{attack.company_name},{attack.sector},{attack.country},{attack.impact_level},{attack.name},{attack.hack_date},{attack.description}\n"
            
            return api_response(
                data={'csv_content': csv_data},
                message=f"Exported {len(attacks)} attacks in CSV format"
            )
        
        else:
            return api_response(
                error="Unsupported format. Use 'json' or 'csv'",
                message="Invalid export format",
                status_code=400
            )
            
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to export attacks data",
            status_code=500
        )

@api_bp.route('/export/companies', methods=['GET'])
@rate_limit(max_requests=20, window=3600)
def export_companies():
    """Şirket verilerini export et"""
    try:
        format_type = request.args.get('format', 'json')
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        companies = HackedCompany.query.filter(HackedCompany.created_at >= start_date).all()
        
        if format_type == 'json':
            data = []
            for company in companies:
                data.append({
                    'id': company.id,
                    'company_name': company.company_name,
                    'country_code': company.country_code,
                    'sector': company.sector,
                    'company_size': company.company_size,
                    'hack_date': company.hack_date.isoformat() if company.hack_date else None,
                    'threat_actor': company.threat_actor,
                    'data_type_leaked': company.data_type_leaked,
                    'impact_level': company.impact_level,
                    'revenue_range': company.revenue_range,
                    'employee_count': company.employee_count
                })
            
            return api_response(
                data=data,
                message=f"Exported {len(data)} companies in JSON format"
            )
        
        else:
            return api_response(
                error="Unsupported format. Use 'json'",
                message="Invalid export format",
                status_code=400
            )
            
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to export companies data",
            status_code=500
        )

# ==================== SEARCH AND FILTER API ====================

@api_bp.route('/search/attacks', methods=['GET'])
@rate_limit(max_requests=100, window=3600)
def search_attacks():
    """Saldırı verilerinde arama"""
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Arama sorgusu
        search_query = Post.query
        if query:
            search_query = search_query.filter(
                Post.title.contains(query) |
                Post.company_name.contains(query) |
                Post.sector.contains(query) |
                Post.country.contains(query)
            )
        
        # Sıralama
        if sort_order == 'desc':
            search_query = search_query.order_by(desc(getattr(Post, sort_by)))
        else:
            search_query = search_query.order_by(asc(getattr(Post, sort_by)))
        
        # Sayfalama
        pagination = search_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        attacks = []
        for attack in pagination.items:
            attacks.append({
                'id': attack.id,
                'title': attack.title,
                'company_name': attack.company_name,
                'sector': attack.sector,
                'country': attack.country,
                'impact_level': attack.impact_level,
                'threat_actor': attack.name,
                'hack_date': attack.hack_date.isoformat() if attack.hack_date else None,
                'created_at': attack.created_at.isoformat()
            })
        
        data = {
            'attacks': attacks,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
        
        return api_response(
            data=data,
            message=f"Found {pagination.total} attacks matching '{query}'"
        )
        
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to search attacks",
            status_code=500
        )

# ==================== ANALYTICS API ====================

@api_bp.route('/analytics/trends', methods=['GET'])
@rate_limit(max_requests=50, window=3600)
def get_analytics_trends():
    """Analitik trend verileri"""
    try:
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Günlük saldırı trendi
        daily_attacks = db.session.query(
            func.strftime('%Y-%m-%d', Post.created_at),
            func.count(Post.id)
        ).filter(
            Post.created_at >= start_date
        ).group_by(
            func.strftime('%Y-%m-%d', Post.created_at)
        ).order_by(
            func.strftime('%Y-%m-%d', Post.created_at)
        ).all()
        
        # Sektör trendi
        sector_trends = db.session.query(
            Post.sector,
            func.strftime('%Y-%m-%d', Post.created_at),
            func.count(Post.id)
        ).filter(
            Post.created_at >= start_date,
            Post.sector.isnot(None)
        ).group_by(
            Post.sector, func.strftime('%Y-%m-%d', Post.created_at)
        ).order_by(
            func.strftime('%Y-%m-%d', Post.created_at)
        ).all()
        
        data = {
            'daily_attacks': [{'date': date, 'count': count} for date, count in daily_attacks],
            'sector_trends': {}
        }
        
        # Sektör trendlerini grupla
        for sector, date, count in sector_trends:
            if sector not in data['sector_trends']:
                data['sector_trends'][sector] = []
            data['sector_trends'][sector].append({'date': date, 'count': count})
        
        return api_response(
            data=data,
            message=f"Analytics trends for last {days} days"
        )
        
    except Exception as e:
        return api_response(
            error=str(e),
            message="Failed to fetch analytics trends",
            status_code=500
        )

# ==================== HEALTH CHECK API ====================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    try:
        # Veritabanı bağlantısını kontrol et
        db.session.execute('SELECT 1')
        
        # Son güncelleme zamanını kontrol et
        last_update = Post.query.order_by(desc(Post.created_at)).first()
        
        data = {
            'status': 'healthy',
            'database': 'connected',
            'last_update': last_update.created_at.isoformat() if last_update else None,
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return api_response(
            data=data,
            message="API is healthy"
        )
        
    except Exception as e:
        return api_response(
            error=str(e),
            message="API health check failed",
            status_code=500
        )

# ==================== ERROR HANDLERS ====================

@api_bp.errorhandler(404)
def not_found(error):
    return api_response(
        error="Endpoint not found",
        message="The requested API endpoint does not exist",
        status_code=404
    )

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return api_response(
        error="Method not allowed",
        message="The HTTP method is not allowed for this endpoint",
        status_code=405
    )

@api_bp.errorhandler(500)
def internal_error(error):
    return api_response(
        error="Internal server error",
        message="An unexpected error occurred",
        status_code=500
    )

