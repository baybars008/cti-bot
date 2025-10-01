# Sosyal Medya İçerik Otomasyon Scripti
# Veri analizi yaparak sosyal medya içerikleri oluşturur

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.DBModel import db, HackedCompany, Post, SocialMediaPost
from utils.sector_detector import SectorDetector

class SocialMediaAutomation:
    def __init__(self):
        self.detector = SectorDetector()
        self.platforms = ['linkedin', 'twitter', 'instagram']
        
        # İçerik template'leri
        self.templates = {
            'linkedin': {
                'weekly_summary': """
🚨 SyberCTI Haftalık Siber Güvenlik Raporu

📊 Bu hafta {total_attacks} şirket saldırıya uğradı
🌍 En çok saldırı alan ülke: {top_country}
🏢 En riskli sektör: {top_sector}
👤 En aktif tehdit aktörü: {top_threat_actor}

🔍 Detaylı analiz için: {dashboard_url}

#SiberGüvenlik #VeriGüvenliği #ThreatIntelligence #TürkiyeSiberGüvenlik
                """,
                'sector_analysis': """
📈 {sector} Sektörü Analizi

⚠️ Bu ay {sector} sektöründe {attack_count} saldırı tespit edildi
📊 Sektör risk skoru: {risk_score}/10
🎯 En çok hedeflenen alt sektör: {sub_sector}
💡 Öneriler: {recommendations}

#SiberGüvenlik #SektörAnalizi #{sector_hashtag}
                """,
                'threat_actor_profile': """
👤 Tehdit Aktörü Profili: {threat_actor}

🎯 Hedef sektörler: {target_sectors}
🌍 Aktif olduğu bölgeler: {active_regions}
📅 Son aktivite: {last_activity}
💼 Saldırı sayısı: {attack_count}

🔍 Daha fazla bilgi için: {profile_url}

#ThreatIntelligence #SiberGüvenlik #TehditAktörü
                """
            },
            'twitter': {
                'quick_stats': """
🚨 SyberCTI Günlük Özet
📊 {total_attacks} saldırı
🌍 {top_country} en riskli
🏢 {top_sector} sektörü hedef
👤 {top_threat_actor} en aktif

#SiberGüvenlik #VeriGüvenliği
                """,
                'breaking_news': """
🚨 BREAKING: {company_name} saldırıya uğradı!
🏢 Sektör: {sector}
🌍 Ülke: {country}
👤 Tehdit: {threat_actor}

#SiberGüvenlik #DataBreach
                """
            },
            'instagram': {
                'infographic_caption': """
🚨 SyberCTI Haftalık Rapor

📊 {total_attacks} şirket saldırıya uğradı
🌍 {top_country} en çok etkilenen ülke
🏢 {top_sector} en riskli sektör
👤 {top_threat_actor} en aktif tehdit aktörü

🔍 Daha fazla bilgi için linke tıklayın!

#SiberGüvenlik #VeriGüvenliği #ThreatIntelligence #TürkiyeSiberGüvenlik #Infographic
                """
            }
        }

    def get_weekly_stats(self, days: int = 7) -> Dict:
        """Haftalık istatistikleri getirir"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Veritabanından veri çek
        posts = Post.query.filter(
            Post.created_at >= start_date,
            Post.created_at <= end_date
        ).all()
        
        # İstatistikleri hesapla
        total_attacks = len(posts)
        
        # Ülke dağılımı
        country_counts = {}
        for post in posts:
            country = post.country or 'Bilinmeyen'
            country_counts[country] = country_counts.get(country, 0) + 1
        
        top_country = max(country_counts, key=country_counts.get) if country_counts else 'Bilinmeyen'
        
        # Sektör dağılımı
        sector_counts = {}
        for post in posts:
            sector = post.sector or 'Bilinmeyen'
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        top_sector = max(sector_counts, key=sector_counts.get) if sector_counts else 'Bilinmeyen'
        
        # Tehdit aktörü dağılımı
        threat_actor_counts = {}
        for post in posts:
            threat_actor = post.name or 'Bilinmeyen'
            threat_actor_counts[threat_actor] = threat_actor_counts.get(threat_actor, 0) + 1
        
        top_threat_actor = max(threat_actor_counts, key=threat_actor_counts.get) if threat_actor_counts else 'Bilinmeyen'
        
        return {
            'total_attacks': total_attacks,
            'top_country': top_country,
            'top_sector': top_sector,
            'top_threat_actor': top_threat_actor,
            'country_distribution': country_counts,
            'sector_distribution': sector_counts,
            'threat_actor_distribution': threat_actor_counts
        }

    def generate_linkedin_content(self, content_type: str, stats: Dict = None) -> str:
        """LinkedIn içerik oluşturur"""
        if not stats:
            stats = self.get_weekly_stats()
        
        template = self.templates['linkedin'].get(content_type, '')
        
        if content_type == 'weekly_summary':
            return template.format(
                total_attacks=stats['total_attacks'],
                top_country=stats['top_country'],
                top_sector=stats['top_sector'],
                top_threat_actor=stats['top_threat_actor'],
                dashboard_url='https://your-dashboard-url.com'
            )
        elif content_type == 'sector_analysis':
            # Sektör analizi için ek veri gerekli
            return template.format(
                sector=stats['top_sector'],
                attack_count=stats['sector_distribution'].get(stats['top_sector'], 0),
                risk_score=8,  # Bu değer hesaplanabilir
                sub_sector='Finansal Hizmetler',  # Bu değer hesaplanabilir
                recommendations='Güçlü kimlik doğrulama ve erişim kontrolü uygulayın',
                sector_hashtag=stats['top_sector'].replace(' ', '').title()
            )
        
        return template

    def generate_twitter_content(self, content_type: str, stats: Dict = None) -> str:
        """Twitter içerik oluşturur"""
        if not stats:
            stats = self.get_weekly_stats()
        
        template = self.templates['twitter'].get(content_type, '')
        
        if content_type == 'quick_stats':
            return template.format(
                total_attacks=stats['total_attacks'],
                top_country=stats['top_country'],
                top_sector=stats['top_sector'],
                top_threat_actor=stats['top_threat_actor']
            )
        elif content_type == 'breaking_news':
            # Son saldırıyı al
            latest_post = Post.query.order_by(Post.created_at.desc()).first()
            if latest_post:
                return template.format(
                    company_name=latest_post.company_name or 'Bilinmeyen Şirket',
                    sector=latest_post.sector or 'Bilinmeyen',
                    country=latest_post.country or 'Bilinmeyen',
                    threat_actor=latest_post.name or 'Bilinmeyen'
                )
        
        return template

    def generate_instagram_content(self, content_type: str, stats: Dict = None) -> str:
        """Instagram içerik oluşturur"""
        if not stats:
            stats = self.get_weekly_stats()
        
        template = self.templates['instagram'].get(content_type, '')
        
        if content_type == 'infographic_caption':
            return template.format(
                total_attacks=stats['total_attacks'],
                top_country=stats['top_country'],
                top_sector=stats['top_sector'],
                top_threat_actor=stats['top_threat_actor']
            )
        
        return template

    def create_social_media_post(self, platform: str, content_type: str, content: str, 
                               image_url: str = None, hashtags: str = None) -> SocialMediaPost:
        """Sosyal medya postu oluşturur ve veritabanına kaydeder"""
        post = SocialMediaPost(
            platform=platform,
            content_type=content_type,
            title=f"{platform.title()} - {content_type.replace('_', ' ').title()}",
            content=content,
            image_url=image_url,
            hashtags=hashtags,
            published_at=datetime.now()
        )
        
        db.session.add(post)
        db.session.commit()
        
        return post

    def generate_weekly_content(self) -> List[SocialMediaPost]:
        """Haftalık içerikleri oluşturur"""
        stats = self.get_weekly_stats()
        posts = []
        
        # LinkedIn haftalık özet
        linkedin_content = self.generate_linkedin_content('weekly_summary', stats)
        linkedin_post = self.create_social_media_post(
            platform='linkedin',
            content_type='weekly_summary',
            content=linkedin_content,
            hashtags='#SiberGüvenlik #VeriGüvenliği #ThreatIntelligence'
        )
        posts.append(linkedin_post)
        
        # Twitter günlük özet
        twitter_content = self.generate_twitter_content('quick_stats', stats)
        twitter_post = self.create_social_media_post(
            platform='twitter',
            content_type='quick_stats',
            content=twitter_content,
            hashtags='#SiberGüvenlik #VeriGüvenliği'
        )
        posts.append(twitter_post)
        
        # Instagram infografik
        instagram_content = self.generate_instagram_content('infographic_caption', stats)
        instagram_post = self.create_social_media_post(
            platform='instagram',
            content_type='infographic_caption',
            content=instagram_content,
            hashtags='#SiberGüvenlik #VeriGüvenliği #Infographic'
        )
        posts.append(instagram_post)
        
        return posts

    def generate_breaking_news_content(self) -> SocialMediaPost:
        """Son saldırı için breaking news içeriği oluşturur"""
        twitter_content = self.generate_twitter_content('breaking_news')
        
        return self.create_social_media_post(
            platform='twitter',
            content_type='breaking_news',
            content=twitter_content,
            hashtags='#SiberGüvenlik #DataBreach #Breaking'
        )

    def get_engagement_metrics(self, post_id: int) -> Dict:
        """Post etkileşim metriklerini getirir (şimdilik mock data)"""
        # Gerçek implementasyonda API'lerden veri çekilecek
        return {
            'likes': 25,
            'shares': 5,
            'comments': 3,
            'views': 150,
            'engagement_rate': 0.22
        }

    def update_post_metrics(self, post_id: int, metrics: Dict):
        """Post metriklerini günceller"""
        post = SocialMediaPost.query.get(post_id)
        if post:
            post.engagement_metrics = json.dumps(metrics)
            db.session.commit()

# Kullanım örneği
if __name__ == "__main__":
    automation = SocialMediaAutomation()
    
    # Haftalık içerikleri oluştur
    weekly_posts = automation.generate_weekly_content()
    print(f"Haftalık {len(weekly_posts)} içerik oluşturuldu")
    
    # Breaking news içeriği oluştur
    breaking_post = automation.generate_breaking_news_content()
    print("Breaking news içeriği oluşturuldu")

