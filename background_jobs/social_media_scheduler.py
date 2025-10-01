# Sosyal Medya İçerik Zamanlayıcısı
# Belirli aralıklarla sosyal medya içerikleri oluşturur ve yayınlar

import sys
import os
import time
import schedule
from datetime import datetime, timedelta

# Proje root'unu path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.social_media_automation import SocialMediaAutomation
from utils.data_analyzer import DataAnalyzer

class SocialMediaScheduler:
    def __init__(self):
        self.automation = SocialMediaAutomation()
        self.analyzer = DataAnalyzer()
        
    def daily_content_generation(self):
        """Günlük içerik üretimi"""
        print(f"[{datetime.now()}] Günlük sosyal medya içerikleri oluşturuluyor...")
        
        try:
            # Günlük istatistikleri al
            stats = self.analyzer.generate_social_media_stats(1)
            
            # Twitter için günlük özet
            twitter_content = self.automation.generate_twitter_content('quick_stats', stats)
            twitter_post = self.automation.create_social_media_post(
                platform='twitter',
                content_type='daily_summary',
                content=twitter_content,
                hashtags='#SiberGüvenlik #VeriGüvenliği #GünlükÖzet'
            )
            print(f"Twitter içeriği oluşturuldu: {twitter_post.id}")
            
            # Eğer yeni saldırı varsa breaking news
            if stats['total_attacks'] > 0:
                breaking_post = self.automation.generate_breaking_news_content()
                print(f"Breaking news içeriği oluşturuldu: {breaking_post.id}")
            
        except Exception as e:
            print(f"Günlük içerik üretiminde hata: {e}")
    
    def weekly_content_generation(self):
        """Haftalık içerik üretimi"""
        print(f"[{datetime.now()}] Haftalık sosyal medya içerikleri oluşturuluyor...")
        
        try:
            # Haftalık içerikleri oluştur
            weekly_posts = self.automation.generate_weekly_content()
            
            for post in weekly_posts:
                print(f"{post.platform.title()} içeriği oluşturuldu: {post.id}")
            
            # Haftalık analiz raporu
            weekly_stats = self.analyzer.generate_social_media_stats(7)
            
            # LinkedIn için detaylı analiz
            linkedin_analysis = self.automation.generate_linkedin_content('sector_analysis', weekly_stats)
            linkedin_post = self.automation.create_social_media_post(
                platform='linkedin',
                content_type='sector_analysis',
                content=linkedin_analysis,
                hashtags='#SiberGüvenlik #SektörAnalizi #HaftalıkRapor'
            )
            print(f"LinkedIn analiz içeriği oluşturuldu: {linkedin_post.id}")
            
        except Exception as e:
            print(f"Haftalık içerik üretiminde hata: {e}")
    
    def monthly_content_generation(self):
        """Aylık içerik üretimi"""
        print(f"[{datetime.now()}] Aylık sosyal medya içerikleri oluşturuluyor...")
        
        try:
            # Aylık istatistikleri al
            monthly_stats = self.analyzer.generate_social_media_stats(30)
            
            # Aylık özet raporu
            monthly_summary = f"""
🚨 SyberCTI Aylık Siber Güvenlik Raporu

📊 Bu ay {monthly_stats['total_attacks']} şirket saldırıya uğradı
🌍 En çok saldırı alan ülke: {monthly_stats['top_country']}
🏢 En riskli sektör: {monthly_stats['top_sector']}
👤 En aktif tehdit aktörü: {monthly_stats['top_threat_actor']}
🇹🇷 Türkiye'deki saldırı sayısı: {monthly_stats['turkey_attacks']}

🔍 Detaylı analiz için dashboard'u ziyaret edin!

#SiberGüvenlik #AylıkRapor #ThreatIntelligence #TürkiyeSiberGüvenlik
            """
            
            # Tüm platformlar için aylık içerik
            for platform in ['linkedin', 'twitter', 'instagram']:
                post = self.automation.create_social_media_post(
                    platform=platform,
                    content_type='monthly_summary',
                    content=monthly_summary,
                    hashtags='#SiberGüvenlik #AylıkRapor #ThreatIntelligence'
                )
                print(f"{platform.title()} aylık içeriği oluşturuldu: {post.id}")
            
        except Exception as e:
            print(f"Aylık içerik üretiminde hata: {e}")
    
    def real_time_breaking_news(self):
        """Gerçek zamanlı breaking news kontrolü"""
        print(f"[{datetime.now()}] Breaking news kontrolü yapılıyor...")
        
        try:
            # Son 1 saatteki yeni saldırıları kontrol et
            recent_stats = self.analyzer.generate_social_media_stats(1)
            
            if recent_stats['total_attacks'] > 0:
                # Breaking news içeriği oluştur
                breaking_post = self.automation.generate_breaking_news_content()
                print(f"Breaking news içeriği oluşturuldu: {breaking_post.id}")
                
                # Discord'a da gönder
                from background_jobs.cron_update_db import send_discord_message
                discord_msg = f"""
🚨 SyberCTI Breaking News

Son 1 saatte {recent_stats['total_attacks']} yeni saldırı tespit edildi!
🌍 En çok etkilenen ülke: {recent_stats['top_country']}
🏢 En riskli sektör: {recent_stats['top_sector']}

Detaylar için sosyal medya hesaplarımızı takip edin!
                """
                send_discord_message(discord_msg)
                
        except Exception as e:
            print(f"Breaking news kontrolünde hata: {e}")
    
    def start_scheduler(self):
        """Zamanlayıcıyı başlatır"""
        print("Sosyal medya zamanlayıcısı başlatılıyor...")
        
        # Günlük görevler
        schedule.every().day.at("09:00").do(self.daily_content_generation)
        schedule.every().day.at("15:00").do(self.daily_content_generation)
        schedule.every().day.at("21:00").do(self.daily_content_generation)
        
        # Haftalık görevler
        schedule.every().monday.at("10:00").do(self.weekly_content_generation)
        schedule.every().friday.at("16:00").do(self.weekly_content_generation)
        
        # Aylık görevler
        schedule.every().month.do(self.monthly_content_generation)
        
        # Gerçek zamanlı görevler (her 30 dakikada bir)
        schedule.every(30).minutes.do(self.real_time_breaking_news)
        
        print("Zamanlayıcı başlatıldı!")
        print("Günlük görevler: 09:00, 15:00, 21:00")
        print("Haftalık görevler: Pazartesi 10:00, Cuma 16:00")
        print("Aylık görevler: Her ayın 1'i")
        print("Gerçek zamanlı: Her 30 dakikada bir")
        
        # Ana döngü
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1 dakika bekle

if __name__ == "__main__":
    scheduler = SocialMediaScheduler()
    scheduler.start_scheduler()

