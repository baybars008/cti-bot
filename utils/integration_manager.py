"""
CTI-BOT Integration Manager
Tüm third-party entegrasyonları yöneten merkezi sistem
"""

from datetime import datetime, timedelta
from utils.slack_integration import slack_integration
from utils.email_integration import email_integration
from utils.teams_integration import teams_integration
from models.DBModel import Post, HackedCompany
from sqlalchemy import func

class IntegrationManager:
    def __init__(self):
        self.integrations = {
            'slack': slack_integration,
            'email': email_integration,
            'teams': teams_integration
        }
        self.notification_preferences = {
            'attack_alerts': ['slack', 'email', 'teams'],
            'daily_summary': ['email'],
            'weekly_report': ['slack', 'email', 'teams'],
            'system_alerts': ['slack', 'teams']
        }
    
    def send_attack_alert(self, attack_data, platforms=None):
        """Saldırı uyarısını belirtilen platformlara gönder"""
        if platforms is None:
            platforms = self.notification_preferences['attack_alerts']
        
        results = {}
        
        for platform in platforms:
            if platform in self.integrations:
                try:
                    if platform == 'slack':
                        success = self.integrations[platform].send_attack_alert(attack_data)
                    elif platform == 'email':
                        # Email için recipient listesi gerekli
                        recipients = self._get_notification_recipients()
                        success = self.integrations[platform].send_attack_alert(recipients, attack_data)
                    elif platform == 'teams':
                        success = self.integrations[platform].send_attack_alert(attack_data)
                    else:
                        success = False
                    
                    results[platform] = {
                        'success': success,
                        'message': 'Başarılı' if success else 'Başarısız'
                    }
                except Exception as e:
                    results[platform] = {
                        'success': False,
                        'message': f'Hata: {str(e)}'
                    }
            else:
                results[platform] = {
                    'success': False,
                    'message': 'Platform bulunamadı'
                }
        
        return results
    
    def send_daily_summary(self, platforms=None):
        """Günlük özeti belirtilen platformlara gönder"""
        if platforms is None:
            platforms = self.notification_preferences['daily_summary']
        
        # Günlük özet verilerini hazırla
        summary_data = self._generate_daily_summary()
        
        results = {}
        
        for platform in platforms:
            if platform in self.integrations:
                try:
                    if platform == 'slack':
                        success = self.integrations[platform].send_daily_summary(summary_data)
                    elif platform == 'email':
                        recipients = self._get_notification_recipients()
                        success = self.integrations[platform].send_daily_summary(recipients, summary_data)
                    elif platform == 'teams':
                        success = self.integrations[platform].send_daily_summary(summary_data)
                    else:
                        success = False
                    
                    results[platform] = {
                        'success': success,
                        'message': 'Başarılı' if success else 'Başarısız'
                    }
                except Exception as e:
                    results[platform] = {
                        'success': False,
                        'message': f'Hata: {str(e)}'
                    }
            else:
                results[platform] = {
                    'success': False,
                    'message': 'Platform bulunamadı'
                }
        
        return results
    
    def send_weekly_report(self, platforms=None):
        """Haftalık raporu belirtilen platformlara gönder"""
        if platforms is None:
            platforms = self.notification_preferences['weekly_report']
        
        # Haftalık rapor verilerini hazırla
        report_data = self._generate_weekly_report()
        
        results = {}
        
        for platform in platforms:
            if platform in self.integrations:
                try:
                    if platform == 'slack':
                        success = self.integrations[platform].send_weekly_report(report_data)
                    elif platform == 'email':
                        recipients = self._get_notification_recipients()
                        success = self.integrations[platform].send_weekly_report(recipients, report_data)
                    elif platform == 'teams':
                        success = self.integrations[platform].send_weekly_report(report_data)
                    else:
                        success = False
                    
                    results[platform] = {
                        'success': success,
                        'message': 'Başarılı' if success else 'Başarısız'
                    }
                except Exception as e:
                    results[platform] = {
                        'success': False,
                        'message': f'Hata: {str(e)}'
                    }
            else:
                results[platform] = {
                    'success': False,
                    'message': 'Platform bulunamadı'
                }
        
        return results
    
    def send_system_alert(self, alert_type, message, severity='info', platforms=None):
        """Sistem uyarısını belirtilen platformlara gönder"""
        if platforms is None:
            platforms = self.notification_preferences['system_alerts']
        
        results = {}
        
        for platform in platforms:
            if platform in self.integrations:
                try:
                    if platform == 'slack':
                        success = self.integrations[platform].send_system_alert(alert_type, message, severity)
                    elif platform == 'email':
                        # Email için sistem uyarısı fonksiyonu eklenebilir
                        success = False
                    elif platform == 'teams':
                        success = self.integrations[platform].send_system_alert(alert_type, message, severity)
                    else:
                        success = False
                    
                    results[platform] = {
                        'success': success,
                        'message': 'Başarılı' if success else 'Başarısız'
                    }
                except Exception as e:
                    results[platform] = {
                        'success': False,
                        'message': f'Hata: {str(e)}'
                    }
            else:
                results[platform] = {
                    'success': False,
                    'message': 'Platform bulunamadı'
                }
        
        return results
    
    def test_all_integrations(self):
        """Tüm entegrasyonları test et"""
        results = {}
        
        for platform, integration in self.integrations.items():
            try:
                test_result = integration.test_connection()
                results[platform] = test_result
            except Exception as e:
                results[platform] = {
                    'status': 'error',
                    'message': f'Test hatası: {str(e)}'
                }
        
        return results
    
    def get_integration_status(self):
        """Tüm entegrasyonların durumunu al"""
        status = {}
        
        for platform, integration in self.integrations.items():
            if hasattr(integration, 'enabled'):
                status[platform] = {
                    'enabled': integration.enabled,
                    'configured': integration.enabled
                }
            else:
                status[platform] = {
                    'enabled': False,
                    'configured': False
                }
        
        return status
    
    def _generate_daily_summary(self):
        """Günlük özet verilerini oluştur"""
        try:
            # Son 24 saat
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=1)
            
            # Temel istatistikler
            total_attacks = Post.query.filter(Post.created_at >= start_date).count()
            unique_companies = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None)
            ).count()
            
            # En çok hedeflenen sektör
            top_sector_query = Post.query.filter(
                Post.created_at >= start_date,
                Post.sector.isnot(None)
            ).with_entities(
                Post.sector, func.count(Post.id)
            ).group_by(Post.sector).order_by(func.count(Post.id).desc()).first()
            
            top_sector = top_sector_query[0] if top_sector_query else 'Bilinmeyen'
            
            # En çok hedeflenen ülke
            top_country_query = Post.query.filter(
                Post.created_at >= start_date,
                Post.country.isnot(None)
            ).with_entities(
                Post.country, func.count(Post.id)
            ).group_by(Post.country).order_by(func.count(Post.id).desc()).first()
            
            top_country = top_country_query[0] if top_country_query else 'Bilinmeyen'
            
            # En aktif tehdit aktörü
            top_threat_actor_query = Post.query.filter(
                Post.created_at >= start_date,
                Post.name.isnot(None)
            ).with_entities(
                Post.name, func.count(Post.id)
            ).group_by(Post.name).order_by(func.count(Post.id).desc()).first()
            
            top_threat_actor = top_threat_actor_query[0] if top_threat_actor_query else 'Bilinmeyen'
            
            # Risk seviyesi dağılımı
            risk_distribution = Post.query.filter(
                Post.created_at >= start_date,
                Post.impact_level.isnot(None)
            ).with_entities(
                Post.impact_level, func.count(Post.id)
            ).group_by(Post.impact_level).all()
            
            risk_counts = {level: count for level, count in risk_distribution}
            
            return {
                'total_attacks': total_attacks,
                'unique_companies': unique_companies,
                'top_sector': top_sector,
                'top_country': top_country,
                'top_threat_actor': top_threat_actor,
                'critical_attacks': risk_counts.get('Kritik', 0),
                'high_attacks': risk_counts.get('Yüksek', 0),
                'medium_attacks': risk_counts.get('Orta', 0),
                'low_attacks': risk_counts.get('Düşük', 0)
            }
            
        except Exception as e:
            print(f"Günlük özet verisi oluşturma hatası: {e}")
            return {
                'total_attacks': 0,
                'unique_companies': 0,
                'top_sector': 'Bilinmeyen',
                'top_country': 'Bilinmeyen',
                'top_threat_actor': 'Bilinmeyen',
                'critical_attacks': 0,
                'high_attacks': 0,
                'medium_attacks': 0,
                'low_attacks': 0
            }
    
    def _generate_weekly_report(self):
        """Haftalık rapor verilerini oluştur"""
        try:
            # Son 7 gün
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            # Haftalık istatistikler
            total_attacks = Post.query.filter(Post.created_at >= start_date).count()
            new_companies = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None)
            ).count()
            
            # En riskli sektör ve ülke
            top_sector_query = Post.query.filter(
                Post.created_at >= start_date,
                Post.sector.isnot(None)
            ).with_entities(
                Post.sector, func.count(Post.id)
            ).group_by(Post.sector).order_by(func.count(Post.id).desc()).first()
            
            top_sector = top_sector_query[0] if top_sector_query else 'Bilinmeyen'
            
            top_country_query = Post.query.filter(
                Post.created_at >= start_date,
                Post.country.isnot(None)
            ).with_entities(
                Post.country, func.count(Post.id)
            ).group_by(Post.country).order_by(func.count(Post.id).desc()).first()
            
            top_country = top_country_query[0] if top_country_query else 'Bilinmeyen'
            
            # Trend analizi (basit)
            previous_week_start = start_date - timedelta(days=7)
            previous_week_attacks = Post.query.filter(
                Post.created_at >= previous_week_start,
                Post.created_at < start_date
            ).count()
            
            trend_change = 0
            if previous_week_attacks > 0:
                trend_change = ((total_attacks - previous_week_attacks) / previous_week_attacks) * 100
            
            return {
                'week_range': f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}",
                'total_attacks': total_attacks,
                'new_companies': new_companies,
                'top_sector': top_sector,
                'top_country': top_country,
                'trend_change': f"{trend_change:+.1f}%",
                'trending_sector': top_sector,
                'trending_country': top_country,
                'report_url': 'http://localhost:5000/'
            }
            
        except Exception as e:
            print(f"Haftalık rapor verisi oluşturma hatası: {e}")
            return {
                'week_range': 'Bu Hafta',
                'total_attacks': 0,
                'new_companies': 0,
                'top_sector': 'Bilinmeyen',
                'top_country': 'Bilinmeyen',
                'trend_change': '0%',
                'trending_sector': 'Bilinmeyen',
                'trending_country': 'Bilinmeyen',
                'report_url': 'http://localhost:5000/'
            }
    
    def _get_notification_recipients(self):
        """Bildirim alıcılarını al"""
        # Bu fonksiyon veritabanından veya konfigürasyondan alıcı listesini alabilir
        # Şimdilik sabit bir liste döndürüyoruz
        import os
        recipients = os.getenv('NOTIFICATION_EMAILS', '').split(',')
        return [email.strip() for email in recipients if email.strip()]

# Global integration manager instance
integration_manager = IntegrationManager()

