# Veri Analizi ve Raporlama Scripti
# Dashboard ve sosyal medya için veri analizi yapar

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
from models.DBModel import db, HackedCompany, Post, Group, Wallet

class DataAnalyzer:
    def __init__(self):
        self.sector_colors = {
            'finans': '#ef4444',      # Kırmızı
            'sağlık': '#f59e0b',      # Turuncu
            'eğitim': '#10b981',      # Yeşil
            'teknoloji': '#3b82f6',   # Mavi
            'e-ticaret': '#8b5cf6',   # Mor
            'enerji': '#f97316',      # Turuncu
            'ulaştırma': '#06b6d4',   # Cyan
            'turizm': '#84cc16',      # Lime
            'gayrimenkul': '#f43f5e', # Pembe
            'medya': '#6366f1',       # İndigo
            'diğer': '#6b7280'        # Gri
        }

    def get_time_range_data(self, days: int = 30) -> Dict:
        """Belirli zaman aralığındaki verileri analiz eder"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Flask app context olmadan doğrudan SQLite kullan
        import sqlite3
        conn = sqlite3.connect('instance/data.db')
        cur = conn.cursor()
        
        # Posts tablosundan veri çek
        cur.execute("SELECT * FROM posts")
        rows = cur.fetchall()
        
        # Sütun isimlerini al
        cur.execute("PRAGMA table_info(posts)")
        columns = [col[1] for col in cur.fetchall()]
        
        # Dict formatına çevir
        posts = []
        for row in rows:
            post_dict = dict(zip(columns, row))
            posts.append(post_dict)
        
        conn.close()
        
        return {
            'posts': posts,
            'start_date': start_date,
            'end_date': end_date,
            'total_count': len(posts)
        }

    def analyze_geographic_distribution(self, days: int = 30) -> Dict:
        """Coğrafi dağılım analizi"""
        # Tüm verileri al (tarih filtresi kaldırıldı)
        data = self.get_time_range_data(days)
        posts = data['posts']
        
        country_counts = Counter()
        for post in posts:
            country = post.get('country') or 'Bilinmeyen'
            country_counts[country] += 1
        
        # En çok saldırı alan 10 ülke
        top_countries = dict(country_counts.most_common(10))
        
        # Türkiye'nin sıralaması
        turkey_rank = None
        if 'TR' in country_counts:
            turkey_rank = list(country_counts.keys()).index('TR') + 1
        
        return {
            'top_countries': top_countries,
            'turkey_rank': turkey_rank,
            'total_countries': len(country_counts),
            'turkey_attacks': country_counts.get('TR', 0)
        }

    def analyze_sector_distribution(self, days: int = 30) -> Dict:
        """Sektörel dağılım analizi - Gerçek şirket sektörleri"""
        # Tüm verileri al (tarih filtresi kaldırıldı)
        posts = Post.query.all()
        
        # Gerçek sektör tespiti
        try:
            from sector_detector import SectorDetector
            detector = SectorDetector()
            sector_analysis = detector.analyze_sectors(posts)
            sector_counts = sector_analysis['sector_counts']
            total_sectors = sector_analysis['total_sectors']
        except ImportError:
            # Fallback: Activity değerlerini kullan
            sector_counts = Counter([post.activity or 'bilinmeyen' for post in posts])
            total_sectors = len(sector_counts)
        
        # Sektörel etki seviyesi (activity'den)
        sector_impact = {}
        for post in posts:
            # Gerçek sektör tespit et
            if 'detector' in locals():
                sector = detector.detect_sector(post.name or '', post.description or '')
            else:
                sector = post.activity or 'bilinmeyen'
            
            if sector not in sector_impact:
                sector_impact[sector] = {'düşük': 0, 'orta': 0, 'yüksek': 0, 'kritik': 0}
            
            # Activity değerini impact olarak kullan
            impact = post.activity or 'orta'
            if impact in sector_impact[sector]:
                sector_impact[sector][impact] += 1
            else:
                sector_impact[sector]['orta'] += 1
        
        # En riskli sektörler (toplam saldırı sayısına göre)
        top_sectors = dict(sector_counts.most_common(10))
        
        # Risk skorları hesapla
        sector_risk_scores = {}
        for sector, count in sector_counts.items():
            impact_data = sector_impact.get(sector, {})
            # Risk skoru: kritik*4 + yüksek*3 + orta*2 + düşük*1
            risk_score = (impact_data.get('kritik', 0) * 4 + 
                         impact_data.get('yüksek', 0) * 3 + 
                         impact_data.get('orta', 0) * 2 + 
                         impact_data.get('düşük', 0) * 1)
            sector_risk_scores[sector] = risk_score
        
        # En riskli sektörler
        top_risky_sectors = dict(sorted(sector_risk_scores.items(), 
                                       key=lambda x: x[1], reverse=True)[:10])
        
        return {
            'sector_counts': top_sectors,
            'sector_risk_scores': top_risky_sectors,
            'sector_impact': sector_impact,
            'total_sectors': len(sector_counts)
        }
    
    def analyze_attack_trends(self, days: int = 30) -> Dict:
        """Saldırı trendleri analizi - Activity değerlerini kullan"""
        # Tüm verileri al
        posts = Post.query.all()
        
        # Activity değerlerini say (saldırı türleri)
        attack_counts = Counter([post.activity or 'bilinmeyen' for post in posts])
        
        # Risk seviyelerine göre grupla
        risk_levels = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Kritik': 0,
            'Yüksek': 0,
            'Orta': 0,
            'Düşük': 0
        }
        
        for activity, count in attack_counts.items():
            if activity in risk_levels:
                risk_levels[activity] = count
        
        # Toplam risk seviyeleri
        total_critical = risk_levels['Critical'] + risk_levels['Kritik']
        total_high = risk_levels['High'] + risk_levels['Yüksek']
        total_medium = risk_levels['Medium'] + risk_levels['Orta']
        total_low = risk_levels['Low'] + risk_levels['Düşük']
        
        return {
            'attack_types': dict(attack_counts),
            'risk_levels': {
                'critical': total_critical,
                'high': total_high,
                'medium': total_medium,
                'low': total_low
            },
            'total_attacks': len(posts),
            'unique_attack_types': len(attack_counts)
        }

    def analyze_threat_actors(self, days: int = 30) -> Dict:
        """Tehdit aktörü analizi"""
        # Tüm verileri al (tarih filtresi kaldırıldı)
        posts = Post.query.all()
        
        threat_actor_counts = Counter()
        threat_actor_sectors = {}
        threat_actor_countries = {}
        
        for post in posts:
            threat_actor = post.name or 'Bilinmeyen'
            threat_actor_counts[threat_actor] += 1
            
            # Tehdit aktörünün hedeflediği sektörler (mevcut tabloda sector yok)
            if threat_actor not in threat_actor_sectors:
                threat_actor_sectors[threat_actor] = Counter()
            sector = 'diğer'  # Mevcut tabloda sector yok
            threat_actor_sectors[threat_actor][sector] += 1
            
            # Tehdit aktörünün aktif olduğu ülkeler
            if threat_actor not in threat_actor_countries:
                threat_actor_countries[threat_actor] = Counter()
            country = post.country or 'Bilinmeyen'
            threat_actor_countries[threat_actor][country] += 1
        
        # En aktif tehdit aktörleri
        top_threat_actors = dict(threat_actor_counts.most_common(10))
        
        return {
            'threat_actor_counts': top_threat_actors,
            'threat_actor_sectors': dict(threat_actor_sectors),
            'threat_actor_countries': dict(threat_actor_countries),
            'total_threat_actors': len(threat_actor_counts)
        }

    def analyze_temporal_trends(self, days: int = 30) -> Dict:
        """Zaman bazlı trend analizi"""
        data = self.get_time_range_data(days)
        posts = data['posts']
        
        # Günlük dağılım
        daily_counts = Counter()
        for post in posts:
            date = post.created_at.date()
            daily_counts[date] += 1
        
        # Haftalık dağılım
        weekly_counts = Counter()
        for post in posts:
            week = post.created_at.isocalendar()[1]  # Hafta numarası
            weekly_counts[week] += 1
        
        # Aylık dağılım
        monthly_counts = Counter()
        for post in posts:
            month = post.created_at.strftime('%Y-%m')
            monthly_counts[month] += 1
        
        return {
            'daily_counts': dict(daily_counts),
            'weekly_counts': dict(weekly_counts),
            'monthly_counts': dict(monthly_counts),
            'peak_day': max(daily_counts, key=daily_counts.get) if daily_counts else None,
            'peak_week': max(weekly_counts, key=weekly_counts.get) if weekly_counts else None
        }

    def analyze_company_characteristics(self, days: int = 30) -> Dict:
        """Şirket karakteristikleri analizi"""
        data = self.get_time_range_data(days)
        posts = data['posts']
        
        company_size_counts = Counter()
        impact_level_counts = Counter()
        data_type_counts = Counter()
        
        for post in posts:
            # Şirket büyüklüğü
            size = post.company_size or 'bilinmeyen'
            company_size_counts[size] += 1
            
            # Etki seviyesi
            impact = post.activity or 'bilinmeyen'  # Mevcut tabloda impact_level yok, activity kullan
            impact_level_counts[impact] += 1
            
            # Veri türü
            data_type = post.data_type_leaked or 'bilinmeyen'
            data_type_counts[data_type] += 1
        
        return {
            'company_size_distribution': dict(company_size_counts),
            'impact_level_distribution': dict(impact_level_counts),
            'data_type_distribution': dict(data_type_counts)
        }

    def generate_dashboard_data(self, days: int = 30) -> Dict:
        """Dashboard için tüm analiz verilerini oluşturur"""
        try:
            # Temel istatistikler
            data = self.get_time_range_data(days)
            posts = data['posts']
            
            # Toplam sayılar
            total_attacks = len(posts)
            total_companies = len(set([p.name for p in posts if p.name]))
            total_countries = len(set([p.country for p in posts if p.country]))
            # Sektör sayısını hesapla (basit yöntem)
            total_sectors = len(set([p.activity for p in posts if p.activity]))
            
            # Risk seviyesi dağılımı (activity sütununu kullan)
            risk_levels = Counter([p.activity for p in posts if p.activity])
            critical_attacks = risk_levels.get('Critical', 0)
            high_attacks = risk_levels.get('High', 0)
            medium_attacks = risk_levels.get('Medium', 0)
            low_attacks = risk_levels.get('Low', 0)
            
            # Coğrafi analiz
            country_counts = Counter([p.country for p in posts if p.country])
            top_countries = dict(country_counts.most_common(10))
            
            # Tehdit aktörü analizi
            threat_actor_counts = Counter([p.name for p in posts if p.name])
            top_threat_actors = dict(threat_actor_counts.most_common(10))
            
            return {
                'overview': {
                    'total_attacks': total_attacks,
                    'total_companies': total_companies,
                    'total_countries': total_countries,
                    'total_sectors': total_sectors,
                    'total_threat_actors': len(top_threat_actors)
                },
                'risk_distribution': {
                    'critical': critical_attacks,
                    'high': high_attacks,
                    'medium': medium_attacks,
                    'low': low_attacks
                },
                'total_attacks': total_attacks,
                'affected_companies': total_companies,
                'affected_countries': total_countries,
                'total_sectors': total_sectors,
                'critical_attacks': critical_attacks,
                'high_attacks': high_attacks,
                'medium_attacks': medium_attacks,
                'low_attacks': low_attacks,
                'risk_level': 'High' if critical_attacks > 0 else 'Medium' if high_attacks > 0 else 'Low',
                'top_countries': top_countries,
                'top_threat_actors': top_threat_actors,
                'geographic': self.analyze_geographic_distribution(days),
                'sector': self.analyze_sector_distribution(days),
                'attack_trends': self.analyze_attack_trends(days),
                'threat_actors': self.analyze_threat_actors(days),
                'temporal': self.analyze_temporal_trends(days),
                'company_characteristics': self.analyze_company_characteristics(days),
                'time_range': {
                    'days': days,
                    'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                    'end_date': datetime.now().strftime('%Y-%m-%d')
                }
            }
        except Exception as e:
            print(f"Dashboard veri oluşturma hatası: {e}")
            return {
                'total_attacks': 0,
                'affected_companies': 0,
                'affected_countries': 0,
                'total_sectors': 0,
                'critical_attacks': 0,
                'high_attacks': 0,
                'medium_attacks': 0,
                'low_attacks': 0,
                'risk_level': 'Unknown',
                'top_countries': {},
                'top_threat_actors': {},
                'error': str(e)
            }

    def generate_social_media_stats(self, days: int = 7) -> Dict:
        """Sosyal medya için özet istatistikler"""
        data = self.get_time_range_data(days)
        posts = data['posts']
        
        if not posts:
            return {
                'total_attacks': 0,
                'top_country': 'Bilinmeyen',
                'top_sector': 'Bilinmeyen',
                'top_threat_actor': 'Bilinmeyen',
                'turkey_attacks': 0,
                'risk_level': 'Düşük'
            }
        
        # Temel istatistikler
        country_counts = Counter(post.country or 'Bilinmeyen' for post in posts)
        sector_counts = Counter('diğer' for post in posts)  # Mevcut tabloda sector yok
        threat_actor_counts = Counter(post.name or 'Bilinmeyen' for post in posts)
        
        # Risk seviyesi hesapla
        high_impact_posts = [post for post in posts if post.activity in ['yüksek', 'kritik', 'High', 'Critical']]  # Mevcut tabloda impact_level yok, activity kullan
        risk_level = 'Yüksek' if len(high_impact_posts) > len(posts) * 0.3 else 'Orta'
        
        return {
            'total_attacks': len(posts),
            'top_country': max(country_counts, key=country_counts.get),
            'top_sector': max(sector_counts, key=sector_counts.get),
            'top_threat_actor': max(threat_actor_counts, key=threat_actor_counts.get),
            'turkey_attacks': country_counts.get('TR', 0),
            'risk_level': risk_level,
            'high_impact_attacks': len(high_impact_posts),
            'sector_distribution': dict(sector_counts.most_common(5)),
            'country_distribution': dict(country_counts.most_common(5))
        }

    def export_to_json(self, data: Dict, filename: str = None) -> str:
        """Veriyi JSON formatında export eder"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'cti_analysis_{timestamp}.json'
        
        # Datetime objelerini string'e çevir
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        # Recursive olarak datetime objelerini dönüştür
        def clean_data(data):
            if isinstance(data, dict):
                return {k: clean_data(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_data(item) for item in data]
            else:
                return convert_datetime(data)
        
        cleaned_data = clean_data(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        return filename

    def generate_chart_data(self, analysis_type: str, days: int = 30) -> Dict:
        """Grafik verilerini oluşturur"""
        if analysis_type == 'geographic':
            data = self.analyze_geographic_distribution(days)
            return {
                'labels': list(data['top_countries'].keys()),
                'values': list(data['top_countries'].values()),
                'colors': [self.sector_colors.get('diğer', '#6b7280')] * len(data['top_countries'])
            }
        elif analysis_type == 'sector':
            data = self.analyze_sector_distribution(days)
            return {
                'labels': list(data['sector_counts'].keys()),
                'values': list(data['sector_counts'].values()),
                'colors': [self.sector_colors.get(sector, '#6b7280') for sector in data['sector_counts'].keys()]
            }
        elif analysis_type == 'threat_actors':
            data = self.analyze_threat_actors(days)
            return {
                'labels': list(data['threat_actor_counts'].keys()),
                'values': list(data['threat_actor_counts'].values()),
                'colors': [self.sector_colors.get('diğer', '#6b7280')] * len(data['threat_actor_counts'])
            }
        
        return {}

    def analyze_timeline_trends(self, days: int = 30) -> Dict:
        """Zaman çizelgesi trend analizi"""
        try:
            # Tüm verileri al (tarih filtresi kaldırıldı)
            posts = Post.query.all()
            
            if not posts:
                return {
                    'daily_counts': {},
                    'weekly_counts': {},
                    'trend': 'stable'
                }
            
            # Günlük saldırı sayılarını hesapla
            daily_counts = {}
            for post in posts:
                if post.discovered:
                    try:
                        date_str = post.discovered[:10]  # YYYY-MM-DD formatı
                        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
                    except:
                        continue
            
            # Haftalık sayıları hesapla
            weekly_counts = {}
            for date_str, count in daily_counts.items():
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    week_start = date_obj - timedelta(days=date_obj.weekday())
                    week_str = week_start.strftime('%Y-%m-%d')
                    weekly_counts[week_str] = weekly_counts.get(week_str, 0) + count
                except:
                    continue
            
            # Trend hesapla
            daily_values = list(daily_counts.values())
            if len(daily_values) >= 2:
                first_half = sum(daily_values[:len(daily_values)//2])
                second_half = sum(daily_values[len(daily_values)//2:])
                if second_half > first_half * 1.1:
                    trend = 'increasing'
                elif second_half < first_half * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            return {
                'daily_counts': daily_counts,
                'weekly_counts': weekly_counts,
                'trend': trend
            }
        except Exception as e:
            return {
                'daily_counts': {},
                'weekly_counts': {},
                'trend': 'stable',
                'error': str(e)
            }

    def get_basic_stats(self, days: int = 30) -> Dict:
        """Temel istatistikleri döndürür - Controller için uyumlu format"""
        try:
            data = self.get_time_range_data(days)
            posts = data['posts']
            
            # Toplam sayılar
            total_attacks = len(posts)
            total_companies = len(set([p.get('name') for p in posts if p.get('name')]))
            total_countries = len(set([p.get('country') for p in posts if p.get('country')]))
            total_sectors = len(set([p.get('activity') for p in posts if p.get('activity')]))
            
            # Risk seviyesi dağılımı
            risk_levels = Counter([p.get('activity') for p in posts if p.get('activity')])
            critical_attacks = risk_levels.get('Critical', 0) + risk_levels.get('Kritik', 0)
            high_attacks = risk_levels.get('High', 0) + risk_levels.get('Yüksek', 0)
            medium_attacks = risk_levels.get('Medium', 0) + risk_levels.get('Orta', 0)
            low_attacks = risk_levels.get('Low', 0) + risk_levels.get('Düşük', 0)
            
            # Coğrafi analiz
            country_counts = Counter([p.get('country') for p in posts if p.get('country')])
            top_countries = dict(country_counts.most_common(10))
            
            # Tehdit aktörü analizi
            threat_actor_counts = Counter([p.get('name') for p in posts if p.get('name')])
            top_threat_actors = dict(threat_actor_counts.most_common(10))
            
            # Sektör analizi (basit)
            sector_counts = Counter([p.get('activity') for p in posts if p.get('activity')])
            real_sectors = dict(sector_counts.most_common(10))
            
            # Activity analizi
            activities = dict(Counter([p.get('activity') for p in posts if p.get('activity')]))
            
            return {
                'overview': {
                    'total_attacks': total_attacks,
                    'total_companies': total_companies,
                    'total_countries': total_countries,
                    'total_sectors': total_sectors,
                    'total_threat_actors': len(top_threat_actors)
                },
                'risk_distribution': {
                    'critical': critical_attacks,
                    'high': high_attacks,
                    'medium': medium_attacks,
                    'low': low_attacks
                },
                'top_countries': top_countries,
                'top_threat_actors': top_threat_actors,
                'real_sectors': real_sectors,
                'activities': activities
            }
        except Exception as e:
            print(f"Basic stats error: {e}")
            return {
                'overview': {
                    'total_attacks': 0,
                    'total_companies': 0,
                    'total_countries': 0,
                    'total_sectors': 0,
                    'total_threat_actors': 0
                },
                'risk_distribution': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                },
                'top_countries': {},
                'top_threat_actors': {},
                'real_sectors': {},
                'activities': {}
            }

    def generate_dashboard_data(self, days: int = 30) -> Dict:
        """Dashboard için ana veri setini oluşturur"""
        try:
            # Temel istatistikler
            data = self.get_time_range_data(days)
            posts = data['posts']
            
            # Toplam sayılar
            total_attacks = len(posts)
            total_companies = len(set([p.name for p in posts if p.name]))
            total_countries = len(set([p.country for p in posts if p.country]))
            # Sektör sayısını hesapla (basit yöntem)
            total_sectors = len(set([p.activity for p in posts if p.activity]))
            
            # Risk seviyesi dağılımı (activity sütununu kullan)
            risk_levels = Counter([p.activity for p in posts if p.activity])
            critical_attacks = risk_levels.get('Critical', 0)
            high_attacks = risk_levels.get('High', 0)
            medium_attacks = risk_levels.get('Medium', 0)
            low_attacks = risk_levels.get('Low', 0)
            
            # Coğrafi analiz
            geo_data = self.analyze_geographic_distribution(days)
            
            # Sektör analizi
            sector_data = self.analyze_sector_distribution(days)
            
            # Tehdit aktörü analizi
            threat_data = self.analyze_threat_actors(days)
            
            # Zaman serisi analizi
            timeline_data = self.analyze_timeline_trends(days)
            
            return {
                'overview': {
                    'total_attacks': total_attacks,
                    'total_companies': total_companies,
                    'total_countries': total_countries,
                    'total_sectors': total_sectors,
                    'period_days': days,
                    'start_date': data['start_date'].isoformat(),
                    'end_date': data['end_date'].isoformat()
                },
                'risk_distribution': {
                    'critical': critical_attacks,
                    'high': high_attacks,
                    'medium': medium_attacks,
                    'low': low_attacks
                },
                'geographic': geo_data,
                'sector': sector_data,
                'threat_actors': threat_data,
                'timeline': timeline_data,
                'charts': {
                    'geographic': self.generate_chart_data('geographic', days),
                    'sector': self.generate_chart_data('sector', days),
                    'threat_actors': self.generate_chart_data('threat_actors', days)
                }
            }
        except Exception as e:
            print(f"Dashboard data generation error: {e}")
            return {
                'overview': {
                    'total_attacks': 0,
                    'total_companies': 0,
                    'total_countries': 0,
                    'total_sectors': 0,
                    'period_days': days,
                    'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
                    'end_date': datetime.now().isoformat()
                },
                'risk_distribution': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                },
                'geographic': {'top_countries': {}, 'country_counts': {}},
                'sector': {'sector_counts': {}, 'sector_percentages': {}},
                'threat_actors': {'threat_actor_counts': {}, 'threat_actor_percentages': {}},
                'timeline': {'daily_counts': {}, 'weekly_counts': {}},
                'charts': {
                    'geographic': {'labels': [], 'values': [], 'colors': []},
                    'sector': {'labels': [], 'values': [], 'colors': []},
                    'threat_actors': {'labels': [], 'values': [], 'colors': []}
                }
            }

# Kullanım örneği
if __name__ == "__main__":
    analyzer = DataAnalyzer()
    
    # Dashboard verilerini oluştur
    dashboard_data = analyzer.generate_dashboard_data(30)
    print("Dashboard verileri oluşturuldu")
    
    # Sosyal medya istatistiklerini oluştur
    social_stats = analyzer.generate_social_media_stats(7)
    print("Sosyal medya istatistikleri oluşturuldu")
    
    # JSON export
    filename = analyzer.export_to_json(dashboard_data)
    print(f"Veriler {filename} dosyasına export edildi")
