# Export Controller - Hafta 6 API Geliştirmeleri
# Export işlemleri için özel controller

from models.DBModel import *
from flask import render_template, jsonify, send_file, make_response, request
from utils.export_generator import ExportGenerator
from datetime import datetime, timedelta
from sqlalchemy import text
import io

def controller_export_attacks():
    """Saldırı verilerini export et"""
    try:
        format_type = request.args.get('format', 'excel')
        days = int(request.args.get('days', 30))
        
        # Filtreler
        filters = {}
        if request.args.get('sector'):
            filters['sector'] = request.args.get('sector')
        if request.args.get('country'):
            filters['country'] = request.args.get('country')
        if request.args.get('impact_level'):
            filters['impact_level'] = request.args.get('impact_level')
        
        # Verileri al
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        posts = Post.query.filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.name.isnot(None)
        ).all()
        
        if format_type == 'excel':
            # Basit Excel export
            import pandas as pd
            
            data = []
            for post in posts:
                data.append({
                    'Company': post.name or 'Unknown',
                    'Country': post.country or 'Unknown',
                    'Activity': post.activity or 'Unknown',
                    'Date': post.discovered or 'Unknown',
                    'Description': post.description or 'Unknown'
                })
            
            df = pd.DataFrame(data)
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            
            filename = f"attacks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        elif format_type == 'csv':
            # CSV export
            csv_data = "Company,Country,Activity,Date,Description\n"
            for post in posts:
                csv_data += f"{post.name or 'Unknown'},{post.country or 'Unknown'},{post.activity or 'Unknown'},{post.discovered or 'Unknown'},{post.description or 'Unknown'}\n"
            
            filename = f"attacks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        
        else:
            return jsonify({
                'success': False,
                'error': 'Desteklenmeyen format. Excel, PDF veya CSV kullanın.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_api_status():
    """API durum bilgisi"""
    try:
        # Veritabanı durumu
        db_status = "connected"
        try:
            db.session.execute(text('SELECT 1'))
        except:
            db_status = "disconnected"
        
        # Son güncelleme
        last_post = Post.query.order_by(Post.discovered.desc()).first()
        last_update = last_post.discovered if last_post else None
        
        # Toplam kayıt sayısı
        total_posts = Post.query.count()
        
        data = {
            'status': 'operational',
            'database': db_status,
            'total_records': total_posts,
            'last_update': last_update,
            'version': '2.1.7',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': 'API is operational'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'API status check failed'
        }), 500

def controller_export_companies():
    """Şirket verilerini export et"""
    try:
        format_type = request.args.get('format', 'excel')
        days = int(request.args.get('days', 30))
        
        # Verileri al
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        posts = Post.query.filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.name.isnot(None)
        ).all()
        
        # Benzersiz şirketleri al
        companies = {}
        for post in posts:
            if post.name:
                companies[post.name] = {
                    'name': post.name,
                    'country': post.country or 'Unknown',
                    'activity': post.activity or 'Unknown',
                    'last_attack': post.discovered or 'Unknown',
                    'website': post.website or 'Unknown'
                }
        
        if format_type == 'excel':
            # Basit Excel export
            import pandas as pd
            
            data = list(companies.values())
            df = pd.DataFrame(data)
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            
            filename = f"companies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        elif format_type == 'csv':
            # CSV export
            csv_data = "Company,Country,Activity,Last Attack,Website\n"
            for company in companies.values():
                csv_data += f"{company['name']},{company['country']},{company['activity']},{company['last_attack']},{company['website']}\n"
            
            filename = f"companies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported format. Use excel or csv.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def controller_api_health():
    """API sağlık kontrolü"""
    try:
        # Veritabanı bağlantısını kontrol et
        db.session.execute(text('SELECT 1'))
        
        # Son güncelleme zamanını kontrol et
        last_update = Post.query.order_by(Post.discovered.desc()).first()
        
        data = {
            'status': 'healthy',
            'database': 'connected',
            'last_update': last_update.discovered if last_update else None,
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': data,
            'message': 'API is healthy'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'API health check failed'
        }), 500

def controller_bulk_export():
    """Toplu export işlemi"""
    try:
        export_type = request.args.get('type', 'all')  # all, attacks, companies
        format_type = request.args.get('format', 'excel')
        days = int(request.args.get('days', 30))
        
        # Verileri al
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        posts = Post.query.filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.name.isnot(None)
        ).all()
        
        if export_type == 'all':
            # Hem saldırıları hem şirketleri export et
            import pandas as pd
            import zipfile
            
            # Saldırı verileri
            attacks_data = []
            for post in posts:
                attacks_data.append({
                    'Company': post.name or 'Unknown',
                    'Country': post.country or 'Unknown',
                    'Activity': post.activity or 'Unknown',
                    'Date': post.discovered or 'Unknown',
                    'Description': post.description or 'Unknown'
                })
            
            # Şirket verileri (benzersiz)
            companies = {}
            for post in posts:
                if post.name:
                    companies[post.name] = {
                        'Company': post.name,
                        'Country': post.country or 'Unknown',
                        'Activity': post.activity or 'Unknown',
                        'Last Attack': post.discovered or 'Unknown',
                        'Website': post.website or 'Unknown'
                    }
            
            # ZIP dosyası oluştur
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Attacks Excel
                attacks_df = pd.DataFrame(attacks_data)
                attacks_output = io.BytesIO()
                attacks_df.to_excel(attacks_output, index=False)
                attacks_output.seek(0)
                zip_file.writestr('attacks.xlsx', attacks_output.getvalue())
                
                # Companies Excel
                companies_df = pd.DataFrame(list(companies.values()))
                companies_output = io.BytesIO()
                companies_df.to_excel(companies_output, index=False)
                companies_output.seek(0)
                zip_file.writestr('companies.xlsx', companies_output.getvalue())
            
            zip_buffer.seek(0)
            filename = f"cti_bot_bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            return send_file(
                zip_buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/zip'
            )
        
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported export type. Use "all".'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
