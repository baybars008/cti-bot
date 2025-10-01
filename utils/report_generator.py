from datetime import datetime, timedelta
from models.DBModel import db, Post, Group, HackedCompany
from utils.data_analyzer import DataAnalyzer
import json
import os
from flask import current_app

class ReportGenerator:
    def __init__(self):
        self.analyzer = DataAnalyzer()
    
    def generate_daily_report(self, date=None):
        """Günlük otomatik rapor oluşturur"""
        if date is None:
            date = datetime.now().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        # Günlük verileri topla
        daily_posts = Post.query.filter(
            Post.created_at >= start_date,
            Post.created_at < end_date
        ).all()
        
        # İstatistikleri hesapla
        total_attacks = len(daily_posts)
        countries = {}
        sectors = {}
        threat_actors = {}
        
        for post in daily_posts:
            # Ülke dağılımı
            country = post.country or 'Bilinmeyen'
            countries[country] = countries.get(country, 0) + 1
            
            # Sektör dağılımı
            sector = post.sector or 'Bilinmeyen'
            sectors[sector] = sectors.get(sector, 0) + 1
            
            # Tehdit aktörü dağılımı
            actor = post.name or 'Bilinmeyen'
            threat_actors[actor] = threat_actors.get(actor, 0) + 1
        
        # En çok etkilenen ülke
        top_country = max(countries.items(), key=lambda x: x[1]) if countries else ('Bilinmeyen', 0)
        
        # En çok etkilenen sektör
        top_sector = max(sectors.items(), key=lambda x: x[1]) if sectors else ('Bilinmeyen', 0)
        
        # En aktif tehdit aktörü
        top_threat_actor = max(threat_actors.items(), key=lambda x: x[1]) if threat_actors else ('Bilinmeyen', 0)
        
        # Risk seviyesi dağılımı
        risk_levels = {}
        for post in daily_posts:
            risk = post.impact_level or 'Orta'
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        # Rapor oluştur
        report = {
            'report_type': 'daily',
            'date': date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_attacks': total_attacks,
                'top_country': {
                    'name': top_country[0],
                    'count': top_country[1]
                },
                'top_sector': {
                    'name': top_sector[0],
                    'count': top_sector[1]
                },
                'top_threat_actor': {
                    'name': top_threat_actor[0],
                    'count': top_threat_actor[1]
                }
            },
            'statistics': {
                'countries': countries,
                'sectors': sectors,
                'threat_actors': threat_actors,
                'risk_levels': risk_levels
            },
            'attacks': [
                {
                    'company': post.company_name or 'Bilinmeyen',
                    'sector': post.sector or 'Bilinmeyen',
                    'country': post.country or 'Bilinmeyen',
                    'threat_actor': post.name or 'Bilinmeyen',
                    'risk_level': post.impact_level or 'Orta',
                    'date': post.created_at.strftime('%Y-%m-%d %H:%M') if post.created_at else 'Bilinmeyen',
                    'description': post.description or 'Detay yok'
                }
                for post in daily_posts
            ]
        }
        
        return report
    
    def generate_weekly_report(self, start_date=None):
        """Haftalık otomatik rapor oluşturur"""
        if start_date is None:
            start_date = datetime.now().date() - timedelta(days=7)
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=7)
        
        # Haftalık verileri topla
        weekly_posts = Post.query.filter(
            Post.created_at >= start_datetime,
            Post.created_at < end_datetime
        ).all()
        
        # Günlük dağılım
        daily_distribution = {}
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            daily_distribution[day_str] = 0
        
        for post in weekly_posts:
            if post.created_at:
                day_str = post.created_at.strftime('%Y-%m-%d')
                if day_str in daily_distribution:
                    daily_distribution[day_str] += 1
        
        # İstatistikleri hesapla
        total_attacks = len(weekly_posts)
        countries = {}
        sectors = {}
        threat_actors = {}
        
        for post in weekly_posts:
            # Ülke dağılımı
            country = post.country or 'Bilinmeyen'
            countries[country] = countries.get(country, 0) + 1
            
            # Sektör dağılımı
            sector = post.sector or 'Bilinmeyen'
            sectors[sector] = sectors.get(sector, 0) + 1
            
            # Tehdit aktörü dağılımı
            actor = post.name or 'Bilinmeyen'
            threat_actors[actor] = threat_actors.get(actor, 0) + 1
        
        # En çok etkilenen ülke
        top_country = max(countries.items(), key=lambda x: x[1]) if countries else ('Bilinmeyen', 0)
        
        # En çok etkilenen sektör
        top_sector = max(sectors.items(), key=lambda x: x[1]) if sectors else ('Bilinmeyen', 0)
        
        # En aktif tehdit aktörü
        top_threat_actor = max(threat_actors.items(), key=lambda x: x[1]) if threat_actors else ('Bilinmeyen', 0)
        
        # Risk seviyesi dağılımı
        risk_levels = {}
        for post in weekly_posts:
            risk = post.impact_level or 'Orta'
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        # Trend analizi
        first_half = sum(daily_distribution[list(daily_distribution.keys())[i]] for i in range(3))
        second_half = sum(daily_distribution[list(daily_distribution.keys())[i]] for i in range(3, 7))
        trend = 'Yükseliş' if second_half > first_half else 'Düşüş' if second_half < first_half else 'Stabil'
        
        # Rapor oluştur
        report = {
            'report_type': 'weekly',
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': (start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_attacks': total_attacks,
                'average_daily': round(total_attacks / 7, 1),
                'top_country': {
                    'name': top_country[0],
                    'count': top_country[1]
                },
                'top_sector': {
                    'name': top_sector[0],
                    'count': top_sector[1]
                },
                'top_threat_actor': {
                    'name': top_threat_actor[0],
                    'count': top_threat_actor[1]
                },
                'trend': trend
            },
            'statistics': {
                'daily_distribution': daily_distribution,
                'countries': countries,
                'sectors': sectors,
                'threat_actors': threat_actors,
                'risk_levels': risk_levels
            },
            'insights': self._generate_insights(weekly_posts, countries, sectors, threat_actors)
        }
        
        return report
    
    def generate_monthly_report(self, year=None, month=None):
        """Aylık otomatik rapor oluşturur"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Aylık verileri topla
        monthly_posts = Post.query.filter(
            Post.created_at >= start_date,
            Post.created_at < end_date
        ).all()
        
        # Haftalık dağılım
        weekly_distribution = {}
        current_week = start_date
        week_num = 1
        while current_week < end_date:
            week_end = min(current_week + timedelta(days=7), end_date)
            weekly_distribution[f'Hafta {week_num}'] = 0
            week_num += 1
            current_week = week_end
        
        for post in monthly_posts:
            if post.created_at:
                week_num = ((post.created_at - start_date).days // 7) + 1
                week_key = f'Hafta {week_num}'
                if week_key in weekly_distribution:
                    weekly_distribution[week_key] += 1
        
        # İstatistikleri hesapla
        total_attacks = len(monthly_posts)
        countries = {}
        sectors = {}
        threat_actors = {}
        
        for post in monthly_posts:
            # Ülke dağılımı
            country = post.country or 'Bilinmeyen'
            countries[country] = countries.get(country, 0) + 1
            
            # Sektör dağılımı
            sector = post.sector or 'Bilinmeyen'
            sectors[sector] = sectors.get(sector, 0) + 1
            
            # Tehdit aktörü dağılımı
            actor = post.name or 'Bilinmeyen'
            threat_actors[actor] = threat_actors.get(actor, 0) + 1
        
        # En çok etkilenen ülke
        top_country = max(countries.items(), key=lambda x: x[1]) if countries else ('Bilinmeyen', 0)
        
        # En çok etkilenen sektör
        top_sector = max(sectors.items(), key=lambda x: x[1]) if sectors else ('Bilinmeyen', 0)
        
        # En aktif tehdit aktörü
        top_threat_actor = max(threat_actors.items(), key=lambda x: x[1]) if threat_actors else ('Bilinmeyen', 0)
        
        # Risk seviyesi dağılımı
        risk_levels = {}
        for post in monthly_posts:
            risk = post.impact_level or 'Orta'
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        # Rapor oluştur
        report = {
            'report_type': 'monthly',
            'year': year,
            'month': month,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_attacks': total_attacks,
                'average_daily': round(total_attacks / 30, 1),
                'top_country': {
                    'name': top_country[0],
                    'count': top_country[1],
                    'percentage': round(top_country[1] / total_attacks * 100, 1) if total_attacks > 0 else 0
                },
                'top_sector': {
                    'name': top_sector[0],
                    'count': top_sector[1],
                    'percentage': round(top_sector[1] / total_attacks * 100, 1) if total_attacks > 0 else 0
                },
                'top_threat_actor': {
                    'name': top_threat_actor[0],
                    'count': top_threat_actor[1],
                    'percentage': round(top_threat_actor[1] / total_attacks * 100, 1) if total_attacks > 0 else 0
                }
            },
            'statistics': {
                'weekly_distribution': weekly_distribution,
                'countries': countries,
                'sectors': sectors,
                'threat_actors': threat_actors,
                'risk_levels': risk_levels
            },
            'insights': self._generate_insights(monthly_posts, countries, sectors, threat_actors)
        }
        
        return report
    
    def _generate_insights(self, posts, countries, sectors, threat_actors):
        """Rapor için öngörüler oluşturur"""
        insights = []
        
        # En riskli ülke
        if countries:
            top_country = max(countries.items(), key=lambda x: x[1])
            insights.append(f"En çok etkilenen ülke: {top_country[0]} ({top_country[1]} saldırı)")
        
        # En riskli sektör
        if sectors:
            top_sector = max(sectors.items(), key=lambda x: x[1])
            insights.append(f"En çok etkilenen sektör: {top_sector[0]} ({top_sector[1]} saldırı)")
        
        # En aktif tehdit aktörü
        if threat_actors:
            top_actor = max(threat_actors.items(), key=lambda x: x[1])
            insights.append(f"En aktif tehdit aktörü: {top_actor[0]} ({top_actor[1]} saldırı)")
        
        # Risk seviyesi analizi
        high_risk_count = sum(1 for post in posts if post.impact_level in ['Yüksek', 'Kritik'])
        if high_risk_count > 0:
            percentage = round(high_risk_count / len(posts) * 100, 1)
            insights.append(f"Yüksek riskli saldırılar: {high_risk_count} (%{percentage})")
        
        return insights
    
    def save_report(self, report, filename=None):
        """Raporu dosyaya kaydeder"""
        if filename is None:
            report_type = report['report_type']
            if report_type == 'daily':
                filename = f"daily_report_{report['date']}.json"
            elif report_type == 'weekly':
                filename = f"weekly_report_{report['start_date']}_to_{report['end_date']}.json"
            elif report_type == 'monthly':
                filename = f"monthly_report_{report['year']}_{report['month']:02d}.json"
        
        # Reports klasörünü oluştur
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Dosyayı kaydet
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def get_report_summary(self, report_type='daily', date=None):
        """Rapor özetini döndürür"""
        if report_type == 'daily':
            report = self.generate_daily_report(date)
        elif report_type == 'weekly':
            report = self.generate_weekly_report(date)
        elif report_type == 'monthly':
            if date:
                year, month = date.year, date.month
            else:
                year, month = datetime.now().year, datetime.now().month
            report = self.generate_monthly_report(year, month)
        else:
            raise ValueError("Geçersiz rapor türü")
        
        return {
            'type': report['report_type'],
            'date': report.get('date', report.get('start_date', f"{report.get('year', '')}-{report.get('month', ''):02d}")),
            'total_attacks': report['summary']['total_attacks'],
            'top_country': report['summary']['top_country']['name'],
            'top_sector': report['summary']['top_sector']['name'],
            'top_threat_actor': report['summary']['top_threat_actor']['name']
        }

