"""
CTI-BOT Advanced Analytics
Gelişmiş analitik ve makine öğrenmesi özellikleri
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import json
from collections import Counter
from models.DBModel import Post, HackedCompany
from sqlalchemy import func, and_

class AdvancedAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
    
    def generate_attack_patterns(self, days=30):
        """Saldırı pattern'lerini analiz et"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Verileri al
            attacks = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None),
                Post.sector.isnot(None),
                Post.country.isnot(None)
            ).all()
            
            if not attacks:
                return {'error': 'No data available for analysis'}
            
            # Pattern analizi
            patterns = {
                'temporal_patterns': self._analyze_temporal_patterns(attacks),
                'geographical_patterns': self._analyze_geographical_patterns(attacks),
                'sector_patterns': self._analyze_sector_patterns(attacks),
                'threat_actor_patterns': self._analyze_threat_actor_patterns(attacks),
                'risk_correlations': self._analyze_risk_correlations(attacks)
            }
            
            return patterns
            
        except Exception as e:
            return {'error': f'Pattern analysis error: {str(e)}'}
    
    def _analyze_temporal_patterns(self, attacks):
        """Zaman bazlı pattern analizi"""
        try:
            # Günlük dağılım
            daily_counts = {}
            hourly_counts = {}
            weekday_counts = {}
            
            for attack in attacks:
                if attack.created_at:
                    # Günlük
                    day = attack.created_at.strftime('%Y-%m-%d')
                    daily_counts[day] = daily_counts.get(day, 0) + 1
                    
                    # Saatlik
                    hour = attack.created_at.hour
                    hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                    
                    # Haftanın günü
                    weekday = attack.created_at.weekday()
                    weekday_counts[weekday] = weekday_counts.get(weekday, 0) + 1
            
            # En aktif günler/saatler
            most_active_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else (None, 0)
            most_active_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (None, 0)
            most_active_weekday = max(weekday_counts.items(), key=lambda x: x[1]) if weekday_counts else (None, 0)
            
            return {
                'daily_distribution': daily_counts,
                'hourly_distribution': hourly_counts,
                'weekday_distribution': weekday_counts,
                'most_active_day': most_active_day[0],
                'most_active_hour': most_active_hour[0],
                'most_active_weekday': most_active_weekday[0],
                'peak_activity': {
                    'day': most_active_day[1],
                    'hour': most_active_hour[1],
                    'weekday': most_active_weekday[1]
                }
            }
            
        except Exception as e:
            return {'error': f'Temporal analysis error: {str(e)}'}
    
    def _analyze_geographical_patterns(self, attacks):
        """Coğrafi pattern analizi"""
        try:
            country_counts = {}
            country_sectors = {}
            country_risk_levels = {}
            
            for attack in attacks:
                if attack.country:
                    country = attack.country
                    country_counts[country] = country_counts.get(country, 0) + 1
                    
                    # Sektör dağılımı
                    if attack.sector:
                        if country not in country_sectors:
                            country_sectors[country] = {}
                        country_sectors[country][attack.sector] = country_sectors[country].get(attack.sector, 0) + 1
                    
                    # Risk seviyesi dağılımı
                    if attack.impact_level:
                        if country not in country_risk_levels:
                            country_risk_levels[country] = {}
                        country_risk_levels[country][attack.impact_level] = country_risk_levels[country].get(attack.impact_level, 0) + 1
            
            # En riskli ülkeler
            top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'country_distribution': country_counts,
                'country_sectors': country_sectors,
                'country_risk_levels': country_risk_levels,
                'top_countries': top_countries,
                'total_countries': len(country_counts)
            }
            
        except Exception as e:
            return {'error': f'Geographical analysis error: {str(e)}'}
    
    def _analyze_sector_patterns(self, attacks):
        """Sektör pattern analizi"""
        try:
            sector_counts = {}
            sector_countries = {}
            sector_risk_levels = {}
            sector_threat_actors = {}
            
            for attack in attacks:
                if attack.sector:
                    sector = attack.sector
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1
                    
                    # Ülke dağılımı
                    if attack.country:
                        if sector not in sector_countries:
                            sector_countries[sector] = {}
                        sector_countries[sector][attack.country] = sector_countries[sector].get(attack.country, 0) + 1
                    
                    # Risk seviyesi dağılımı
                    if attack.impact_level:
                        if sector not in sector_risk_levels:
                            sector_risk_levels[sector] = {}
                        sector_risk_levels[sector][attack.impact_level] = sector_risk_levels[sector].get(attack.impact_level, 0) + 1
                    
                    # Tehdit aktörü dağılımı
                    if attack.name:
                        if sector not in sector_threat_actors:
                            sector_threat_actors[sector] = {}
                        sector_threat_actors[sector][attack.name] = sector_threat_actors[sector].get(attack.name, 0) + 1
            
            # En riskli sektörler
            top_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'sector_distribution': sector_counts,
                'sector_countries': sector_countries,
                'sector_risk_levels': sector_risk_levels,
                'sector_threat_actors': sector_threat_actors,
                'top_sectors': top_sectors,
                'total_sectors': len(sector_counts)
            }
            
        except Exception as e:
            return {'error': f'Sector analysis error: {str(e)}'}
    
    def _analyze_threat_actor_patterns(self, attacks):
        """Tehdit aktörü pattern analizi"""
        try:
            actor_counts = {}
            actor_sectors = {}
            actor_countries = {}
            actor_risk_levels = {}
            
            for attack in attacks:
                if attack.name:
                    actor = attack.name
                    actor_counts[actor] = actor_counts.get(actor, 0) + 1
                    
                    # Sektör dağılımı
                    if attack.sector:
                        if actor not in actor_sectors:
                            actor_sectors[actor] = {}
                        actor_sectors[actor][attack.sector] = actor_sectors[actor].get(attack.sector, 0) + 1
                    
                    # Ülke dağılımı
                    if attack.country:
                        if actor not in actor_countries:
                            actor_countries[actor] = {}
                        actor_countries[actor][attack.country] = actor_countries[actor].get(attack.country, 0) + 1
                    
                    # Risk seviyesi dağılımı
                    if attack.impact_level:
                        if actor not in actor_risk_levels:
                            actor_risk_levels[actor] = {}
                        actor_risk_levels[actor][attack.impact_level] = actor_risk_levels[actor].get(attack.impact_level, 0) + 1
            
            # En aktif tehdit aktörleri
            top_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'actor_distribution': actor_counts,
                'actor_sectors': actor_sectors,
                'actor_countries': actor_countries,
                'actor_risk_levels': actor_risk_levels,
                'top_actors': top_actors,
                'total_actors': len(actor_counts)
            }
            
        except Exception as e:
            return {'error': f'Threat actor analysis error: {str(e)}'}
    
    def _analyze_risk_correlations(self, attacks):
        """Risk korelasyon analizi"""
        try:
            # Risk seviyesi dağılımı
            risk_levels = {}
            sector_risk_correlation = {}
            country_risk_correlation = {}
            
            for attack in attacks:
                if attack.impact_level:
                    risk = attack.impact_level
                    risk_levels[risk] = risk_levels.get(risk, 0) + 1
                    
                    # Sektör-risk korelasyonu
                    if attack.sector:
                        if attack.sector not in sector_risk_correlation:
                            sector_risk_correlation[attack.sector] = {}
                        sector_risk_correlation[attack.sector][risk] = sector_risk_correlation[attack.sector].get(risk, 0) + 1
                    
                    # Ülke-risk korelasyonu
                    if attack.country:
                        if attack.country not in country_risk_correlation:
                            country_risk_correlation[attack.country] = {}
                        country_risk_correlation[attack.country][risk] = country_risk_correlation[attack.country].get(risk, 0) + 1
            
            # En riskli sektörler (kritik saldırı oranı)
            sector_risk_scores = {}
            for sector, risks in sector_risk_correlation.items():
                total = sum(risks.values())
                critical = risks.get('Kritik', 0)
                high = risks.get('Yüksek', 0)
                risk_score = ((critical * 4) + (high * 2)) / total if total > 0 else 0
                sector_risk_scores[sector] = risk_score
            
            top_risk_sectors = sorted(sector_risk_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'risk_level_distribution': risk_levels,
                'sector_risk_correlation': sector_risk_correlation,
                'country_risk_correlation': country_risk_correlation,
                'sector_risk_scores': sector_risk_scores,
                'top_risk_sectors': top_risk_sectors
            }
            
        except Exception as e:
            return {'error': f'Risk correlation analysis error: {str(e)}'}
    
    def detect_anomalies(self, days=30):
        """Anomali tespiti"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Verileri al
            attacks = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None),
                Post.sector.isnot(None),
                Post.country.isnot(None)
            ).all()
            
            if len(attacks) < 10:
                return {'error': 'Insufficient data for anomaly detection'}
            
            # Veri hazırlama
            data = []
            for attack in attacks:
                data.append({
                    'sector': attack.sector,
                    'country': attack.country,
                    'impact_level': attack.impact_level,
                    'hour': attack.created_at.hour if attack.created_at else 0,
                    'weekday': attack.created_at.weekday() if attack.created_at else 0
                })
            
            df = pd.DataFrame(data)
            
            # Kategorik değişkenleri sayısal değerlere çevir
            df_encoded = pd.get_dummies(df, columns=['sector', 'country', 'impact_level'])
            
            # Anomali tespiti
            anomaly_scores = self.isolation_forest.fit_predict(df_encoded)
            anomalies = df[anomaly_scores == -1]
            
            return {
                'total_attacks': len(attacks),
                'anomalies_detected': len(anomalies),
                'anomaly_rate': len(anomalies) / len(attacks) * 100,
                'anomaly_details': anomalies.to_dict('records') if not anomalies.empty else []
            }
            
        except Exception as e:
            return {'error': f'Anomaly detection error: {str(e)}'}
    
    def generate_predictions(self, days=30):
        """Gelecek tahminleri"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Geçmiş verileri al
            attacks = Post.query.filter(
                Post.created_at >= start_date,
                Post.company_name.isnot(None)
            ).all()
            
            if len(attacks) < 7:
                return {'error': 'Insufficient data for predictions'}
            
            # Günlük saldırı sayıları
            daily_counts = {}
            for attack in attacks:
                if attack.created_at:
                    day = attack.created_at.strftime('%Y-%m-%d')
                    daily_counts[day] = daily_counts.get(day, 0) + 1
            
            # Basit trend analizi
            days_list = sorted(daily_counts.keys())
            counts_list = [daily_counts[day] for day in days_list]
            
            if len(counts_list) < 3:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Linear trend hesaplama
            x = np.arange(len(counts_list))
            y = np.array(counts_list)
            
            # Basit linear regression
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x * x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Gelecek 7 gün tahmini
            future_predictions = []
            for i in range(7):
                future_day = (datetime.strptime(days_list[-1], '%Y-%m-%d') + timedelta(days=i+1)).strftime('%Y-%m-%d')
                predicted_count = max(0, int(slope * (len(counts_list) + i) + intercept))
                future_predictions.append({
                    'date': future_day,
                    'predicted_attacks': predicted_count
                })
            
            # Trend analizi
            recent_avg = np.mean(counts_list[-7:]) if len(counts_list) >= 7 else np.mean(counts_list)
            overall_avg = np.mean(counts_list)
            
            trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            trend_strength = abs(slope) * 100  # Yüzde olarak
            
            return {
                'future_predictions': future_predictions,
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 2),
                'recent_average': round(recent_avg, 2),
                'overall_average': round(overall_avg, 2),
                'confidence_level': min(95, max(50, 100 - trend_strength))
            }
            
        except Exception as e:
            return {'error': f'Prediction error: {str(e)}'}
    
    def generate_insights(self, days=30):
        """Akıllı öngörüler oluştur"""
        try:
            patterns = self.generate_attack_patterns(days)
            anomalies = self.detect_anomalies(days)
            predictions = self.generate_predictions(days)
            
            insights = []
            
            # Pattern insights
            if 'temporal_patterns' in patterns and 'most_active_hour' in patterns['temporal_patterns']:
                most_active_hour = patterns['temporal_patterns']['most_active_hour']
                if most_active_hour is not None:
                    insights.append({
                        'type': 'temporal',
                        'title': 'En Aktif Saat',
                        'description': f'Saldırıların çoğu {most_active_hour}:00 saatinde gerçekleşiyor',
                        'severity': 'info'
                    })
            
            if 'geographical_patterns' in patterns and 'top_countries' in patterns['geographical_patterns']:
                top_countries = patterns['geographical_patterns']['top_countries']
                if top_countries:
                    top_country = top_countries[0]
                    insights.append({
                        'type': 'geographical',
                        'title': 'En Riskli Ülke',
                        'description': f'{top_country[0]} ülkesi {top_country[1]} saldırı ile en çok hedeflenen ülke',
                        'severity': 'warning'
                    })
            
            if 'sector_patterns' in patterns and 'top_sectors' in patterns['sector_patterns']:
                top_sectors = patterns['sector_patterns']['top_sectors']
                if top_sectors:
                    top_sector = top_sectors[0]
                    insights.append({
                        'type': 'sector',
                        'title': 'En Riskli Sektör',
                        'description': f'{top_sector[0]} sektörü {top_sector[1]} saldırı ile en çok hedeflenen sektör',
                        'severity': 'warning'
                    })
            
            # Anomaly insights
            if 'anomaly_rate' in anomalies:
                anomaly_rate = anomalies['anomaly_rate']
                if anomaly_rate > 10:
                    insights.append({
                        'type': 'anomaly',
                        'title': 'Yüksek Anomali Oranı',
                        'description': f'%{anomaly_rate:.1f} anomali oranı tespit edildi',
                        'severity': 'critical'
                    })
            
            # Prediction insights
            if 'trend_direction' in predictions:
                trend_direction = predictions['trend_direction']
                if trend_direction == 'increasing':
                    insights.append({
                        'type': 'prediction',
                        'title': 'Artış Trendi',
                        'description': 'Saldırı sayılarında artış trendi tespit edildi',
                        'severity': 'warning'
                    })
                elif trend_direction == 'decreasing':
                    insights.append({
                        'type': 'prediction',
                        'title': 'Azalış Trendi',
                        'description': 'Saldırı sayılarında azalış trendi tespit edildi',
                        'severity': 'info'
                    })
            
            return {
                'insights': insights,
                'total_insights': len(insights),
                'critical_insights': len([i for i in insights if i['severity'] == 'critical']),
                'warning_insights': len([i for i in insights if i['severity'] == 'warning']),
                'info_insights': len([i for i in insights if i['severity'] == 'info']),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Insights generation error: {str(e)}'}

# Global analytics instance
advanced_analytics = AdvancedAnalytics()

