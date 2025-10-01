from datetime import datetime, timedelta
from models.DBModel import db, Post
from sqlalchemy import func
import json

class AdvancedCharts:
    def __init__(self):
        pass
    
    def generate_heatmap_data(self, days=30):
        """Coğrafi heatmap verisi oluşturur"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Ülke bazında saldırı sayıları
        country_attacks = db.session.query(
            Post.country, func.count(Post.id)
        ).filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d').strftime('%Y-%m-%d'),
            Post.country.isnot(None)
        ).group_by(Post.country).all()
        
        # Ülke koordinatları (örnek veri)
        country_coordinates = {
            'TR': {'lat': 39.9334, 'lng': 32.8597, 'name': 'Türkiye'},
            'US': {'lat': 39.8283, 'lng': -98.5795, 'name': 'Amerika Birleşik Devletleri'},
            'UK': {'lat': 55.3781, 'lng': -3.4360, 'name': 'Birleşik Krallık'},
            'DE': {'lat': 51.1657, 'lng': 10.4515, 'name': 'Almanya'},
            'FR': {'lat': 46.2276, 'lng': 2.2137, 'name': 'Fransa'},
            'IT': {'lat': 41.8719, 'lng': 12.5674, 'name': 'İtalya'},
            'ES': {'lat': 40.4637, 'lng': -3.7492, 'name': 'İspanya'},
            'NL': {'lat': 52.1326, 'lng': 5.2913, 'name': 'Hollanda'},
            'CA': {'lat': 56.1304, 'lng': -106.3468, 'name': 'Kanada'},
            'AU': {'lat': -25.2744, 'lng': 133.7751, 'name': 'Avustralya'},
            'JP': {'lat': 36.2048, 'lng': 138.2529, 'name': 'Japonya'},
            'BR': {'lat': -14.2350, 'lng': -51.9253, 'name': 'Brezilya'},
            'IN': {'lat': 20.5937, 'lng': 78.9629, 'name': 'Hindistan'},
            'CN': {'lat': 35.8617, 'lng': 104.1954, 'name': 'Çin'},
            'RU': {'lat': 61.5240, 'lng': 105.3188, 'name': 'Rusya'}
        }
        
        heatmap_data = []
        max_attacks = max(country_attacks, key=lambda x: x[1])[1] if country_attacks else 1
        
        for country, count in country_attacks:
            if country in country_coordinates:
                coords = country_coordinates[country]
                intensity = count / max_attacks  # 0-1 arası normalize edilmiş değer
                
                heatmap_data.append({
                    'lat': coords['lat'],
                    'lng': coords['lng'],
                    'intensity': intensity,
                    'count': count,
                    'country': country,
                    'name': coords['name']
                })
        
        return {
            'data': heatmap_data,
            'max_intensity': max_attacks,
            'total_countries': len(heatmap_data)
        }
    
    def generate_timeline_heatmap(self, days=90):
        """Zaman çizelgesi heatmap verisi oluşturur"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Günlük saldırı sayıları
        daily_attacks = db.session.query(
            func.strftime('%Y-%m-%d', Post.discovered), func.count(Post.id)
        ).filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d')
        ).group_by(func.strftime('%Y-%m-%d', Post.discovered)).all()
        
        # Haftalık dağılım
        weekly_data = {}
        for date_str, count in daily_attacks:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            week_start = date_obj - timedelta(days=date_obj.weekday())
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {}
            
            day_name = date_obj.strftime('%A')
            weekly_data[week_key][day_name] = count
        
        # Hafta günleri sırası
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Heatmap verisi oluştur
        heatmap_data = []
        for week_start, week_data in weekly_data.items():
            for day in days_order:
                count = week_data.get(day, 0)
                heatmap_data.append({
                    'week': week_start,
                    'day': day,
                    'count': count
                })
        
        return {
            'data': heatmap_data,
            'days_order': days_order,
            'weeks': list(weekly_data.keys())
        }
    
    def generate_sector_radar_chart(self, days=30):
        """Sektörel radar grafik verisi oluşturur"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Sektör bazında saldırı sayıları
        sector_attacks = db.session.query(
            Post.sector, func.count(Post.id)
        ).filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.sector.isnot(None)
        ).group_by(Post.sector).all()
        
        # Risk seviyesi bazında dağılım
        risk_levels = ['Düşük', 'Orta', 'Yüksek', 'Kritik']
        sector_risk_data = {}
        
        for sector, _ in sector_attacks:
            sector_risk_data[sector] = {}
            for risk in risk_levels:
                count = db.session.query(func.count(Post.id)).filter(
                    Post.discovered >= start_date,
                    Post.sector == sector,
                    Post.impact_level == risk
                ).scalar()
                sector_risk_data[sector][risk] = count or 0
        
        # Radar chart verisi
        radar_data = []
        for sector, total_attacks in sector_attacks:
            if total_attacks > 0:  # Sadece saldırı olan sektörler
                radar_data.append({
                    'sector': sector,
                    'total_attacks': total_attacks,
                    'risk_distribution': sector_risk_data.get(sector, {}),
                    'risk_score': self._calculate_risk_score(sector_risk_data.get(sector, {}))
                })
        
        return {
            'data': radar_data,
            'risk_levels': risk_levels,
            'max_attacks': max(sector_attacks, key=lambda x: x[1])[1] if sector_attacks else 1
        }
    
    def generate_threat_actor_network(self, days=30):
        """Tehdit aktörü ağ grafiği verisi oluşturur"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Tehdit aktörü - sektör ilişkileri
        actor_sector_relations = db.session.query(
            Post.name, Post.sector, func.count(Post.id)
        ).filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.name.isnot(None),
            Post.sector.isnot(None)
        ).group_by(Post.name, Post.sector).all()
        
        # Tehdit aktörü - ülke ilişkileri
        actor_country_relations = db.session.query(
            Post.name, Post.country, func.count(Post.id)
        ).filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.name.isnot(None),
            Post.country.isnot(None)
        ).group_by(Post.name, Post.country).all()
        
        # Düğümler (nodes)
        nodes = []
        node_id = 0
        
        # Tehdit aktörleri
        actors = set()
        for actor, _, _ in actor_sector_relations:
            actors.add(actor)
        
        for actor in actors:
            total_attacks = db.session.query(func.count(Post.id)).filter(
                Post.discovered >= start_date,
                Post.name == actor
            ).scalar()
            
            nodes.append({
                'id': node_id,
                'label': actor,
                'group': 'threat_actor',
                'size': min(total_attacks * 2, 50),  # Maksimum 50
                'attacks': total_attacks
            })
            node_id += 1
        
        # Sektörler
        sectors = set()
        for _, sector, _ in actor_sector_relations:
            sectors.add(sector)
        
        for sector in sectors:
            total_attacks = db.session.query(func.count(Post.id)).filter(
                Post.discovered >= start_date,
                Post.sector == sector
            ).scalar()
            
            nodes.append({
                'id': node_id,
                'label': sector,
                'group': 'sector',
                'size': min(total_attacks, 30),  # Maksimum 30
                'attacks': total_attacks
            })
            node_id += 1
        
        # Kenarlar (edges)
        edges = []
        actor_id_map = {node['label']: node['id'] for node in nodes if node['group'] == 'threat_actor'}
        sector_id_map = {node['label']: node['id'] for node in nodes if node['group'] == 'sector'}
        
        for actor, sector, count in actor_sector_relations:
            if actor in actor_id_map and sector in sector_id_map:
                edges.append({
                    'from': actor_id_map[actor],
                    'to': sector_id_map[sector],
                    'width': min(count * 2, 10),  # Maksimum 10
                    'attacks': count
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_actors': len(actors),
            'total_sectors': len(sectors)
        }
    
    def generate_risk_trend_analysis(self, days=90):
        """Risk trend analizi oluşturur"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Haftalık risk seviyesi dağılımı
        weekly_risk_data = {}
        
        for i in range(0, days, 7):
            week_start = start_date + timedelta(days=i)
            week_end = min(week_start + timedelta(days=7), end_date)
            
            week_key = week_start.strftime('%Y-%m-%d')
            
            risk_levels = ['Düşük', 'Orta', 'Yüksek', 'Kritik']
            week_risks = {}
            
            for risk in risk_levels:
                count = db.session.query(func.count(Post.id)).filter(
                    Post.discovered >= week_start,
                    Post.discovered < week_end,
                    Post.impact_level == risk
                ).scalar()
                week_risks[risk] = count or 0
            
            weekly_risk_data[week_key] = week_risks
        
        # Risk skoru hesapla (her hafta için)
        risk_scores = []
        for week, risks in weekly_risk_data.items():
            # Risk skoru: Düşük=1, Orta=3, Yüksek=5, Kritik=7
            score = (risks['Düşük'] * 1 + 
                    risks['Orta'] * 3 + 
                    risks['Yüksek'] * 5 + 
                    risks['Kritik'] * 7)
            
            total_attacks = sum(risks.values())
            avg_score = score / total_attacks if total_attacks > 0 else 0
            
            risk_scores.append({
                'week': week,
                'score': round(avg_score, 2),
                'total_attacks': total_attacks,
                'risk_distribution': risks
            })
        
        # Trend analizi
        if len(risk_scores) >= 2:
            first_half_avg = sum(score['score'] for score in risk_scores[:len(risk_scores)//2]) / (len(risk_scores)//2)
            second_half_avg = sum(score['score'] for score in risk_scores[len(risk_scores)//2:]) / (len(risk_scores) - len(risk_scores)//2)
            
            if second_half_avg > first_half_avg * 1.1:
                trend = 'Yükseliş'
            elif second_half_avg < first_half_avg * 0.9:
                trend = 'Düşüş'
            else:
                trend = 'Stabil'
        else:
            trend = 'Belirsiz'
        
        return {
            'risk_scores': risk_scores,
            'trend': trend,
            'current_week_score': risk_scores[-1]['score'] if risk_scores else 0,
            'average_score': sum(score['score'] for score in risk_scores) / len(risk_scores) if risk_scores else 0
        }
    
    def generate_company_risk_matrix(self, days=30):
        """Şirket risk matrisi oluşturur"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Şirket bazında veriler
        company_data = db.session.query(
            Post.company_name, Post.sector, Post.company_size, 
            Post.impact_level, func.count(Post.id)
        ).filter(
            Post.discovered >= start_date.strftime('%Y-%m-%d'),
            Post.company_name.isnot(None)
        ).group_by(
            Post.company_name, Post.sector, Post.company_size, Post.impact_level
        ).all()
        
        # Şirket risk matrisi
        risk_matrix = {}
        
        for company, sector, size, risk_level, count in company_data:
            if company not in risk_matrix:
                risk_matrix[company] = {
                    'company': company,
                    'sector': sector,
                    'size': size,
                    'total_attacks': 0,
                    'risk_distribution': {'Düşük': 0, 'Orta': 0, 'Yüksek': 0, 'Kritik': 0},
                    'risk_score': 0
                }
            
            risk_matrix[company]['total_attacks'] += count
            risk_matrix[company]['risk_distribution'][risk_level] += count
        
        # Risk skoru hesapla
        for company in risk_matrix.values():
            risk_score = (company['risk_distribution']['Düşük'] * 1 +
                         company['risk_distribution']['Orta'] * 3 +
                         company['risk_distribution']['Yüksek'] * 5 +
                         company['risk_distribution']['Kritik'] * 7)
            
            company['risk_score'] = risk_score / company['total_attacks'] if company['total_attacks'] > 0 else 0
        
        # Matris verisi
        matrix_data = []
        for company in risk_matrix.values():
            matrix_data.append({
                'company': company['company'],
                'sector': company['sector'],
                'size': company['size'],
                'total_attacks': company['total_attacks'],
                'risk_score': round(company['risk_score'], 2),
                'risk_level': self._get_risk_level_from_score(company['risk_score']),
                'risk_distribution': company['risk_distribution']
            })
        
        # Risk seviyesine göre sırala
        matrix_data.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            'data': matrix_data,
            'total_companies': len(matrix_data),
            'high_risk_companies': len([c for c in matrix_data if c['risk_score'] >= 5]),
            'critical_companies': len([c for c in matrix_data if c['risk_score'] >= 6])
        }
    
    def _calculate_risk_score(self, risk_distribution):
        """Risk dağılımından risk skoru hesaplar"""
        total = sum(risk_distribution.values())
        if total == 0:
            return 0
        
        score = (risk_distribution.get('Düşük', 0) * 1 +
                risk_distribution.get('Orta', 0) * 3 +
                risk_distribution.get('Yüksek', 0) * 5 +
                risk_distribution.get('Kritik', 0) * 7)
        
        return score / total
    
    def _get_risk_level_from_score(self, score):
        """Risk skorundan risk seviyesi belirler"""
        if score >= 6:
            return 'Kritik'
        elif score >= 4:
            return 'Yüksek'
        elif score >= 2:
            return 'Orta'
        else:
            return 'Düşük'
