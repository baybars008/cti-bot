import threading
import time
from datetime import datetime, timedelta
from models.DBModel import db, Post
from utils.report_generator import ReportGenerator
from utils.social_media_automation import SocialMediaAutomation
from utils.data_analyzer import DataAnalyzer
import json
import os

class RealtimeUpdater:
    def __init__(self, app=None):
        self.app = app
        self.is_running = False
        self.update_interval = 300  # 5 dakika
        self.last_update = None
        self.report_generator = ReportGenerator()
        self.social_automation = SocialMediaAutomation()
        self.data_analyzer = DataAnalyzer()
        self.update_thread = None
        
    def start(self):
        """Real-time güncellemeleri başlatır"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        print(f"[{datetime.now()}] Real-time güncellemeler başlatıldı (her {self.update_interval} saniyede bir)")
    
    def stop(self):
        """Real-time güncellemeleri durdurur"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        print(f"[{datetime.now()}] Real-time güncellemeler durduruldu")
    
    def _update_loop(self):
        """Güncelleme döngüsü"""
        while self.is_running:
            try:
                self._perform_update()
                self.last_update = datetime.now()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"[{datetime.now()}] Güncelleme hatası: {e}")
                time.sleep(60)  # Hata durumunda 1 dakika bekle
    
    def _perform_update(self):
        """Güncelleme işlemlerini gerçekleştirir"""
        with self.app.app_context():
            # Son güncelleme zamanını kontrol et
            if self.last_update:
                # Son güncellemeden bu yana yeni veri var mı?
                new_posts = Post.query.filter(
                    Post.discovered > self.last_update
                ).count()
                
                if new_posts > 0:
                    print(f"[{datetime.now()}] {new_posts} yeni saldırı tespit edildi")
                    
                    # Dashboard verilerini güncelle
                    self._update_dashboard_cache()
                    
                    # Sosyal medya içeriği oluştur
                    self._generate_social_content()
                    
                    # Kritik saldırıları kontrol et
                    self._check_critical_attacks()
                    
                    # Günlük raporu güncelle
                    self._update_daily_report()
                else:
                    print(f"[{datetime.now()}] Yeni veri yok, güncelleme atlandı")
            else:
                # İlk güncelleme
                print(f"[{datetime.now()}] İlk güncelleme yapılıyor...")
                self._update_dashboard_cache()
                self.last_update = datetime.now()
    
    def _update_dashboard_cache(self):
        """Dashboard cache'ini günceller"""
        try:
            # Son 30 günlük verileri al
            dashboard_data = self.data_analyzer.generate_dashboard_data(30)
            
            # Cache dosyasına kaydet
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_file = os.path.join(cache_dir, 'dashboard_data.json')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'data': dashboard_data,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            print(f"[{datetime.now()}] Dashboard cache güncellendi")
            
        except Exception as e:
            print(f"[{datetime.now()}] Dashboard cache güncelleme hatası: {e}")
    
    def _generate_social_content(self):
        """Sosyal medya içeriği oluşturur"""
        try:
            # Son 24 saatteki verileri al
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            
            recent_posts = Post.query.filter(
                Post.discovered >= start_date,
                Post.discovered <= end_date
            ).all()
            
            if recent_posts:
                # En önemli saldırıyı bul
                critical_attack = None
                for post in recent_posts:
                    if post.impact_level in ['Yüksek', 'Kritik']:
                        critical_attack = post
                        break
                
                if critical_attack:
                    # Breaking news içeriği oluştur
                    post_data = {
                        'company_name': critical_attack.company_name or 'Bilinmeyen Şirket',
                        'country': critical_attack.country or 'Bilinmeyen',
                        'sector': critical_attack.sector or 'Bilinmeyen',
                        'threat_actor': critical_attack.name or 'Bilinmeyen Aktör',
                        'data_type_leaked': critical_attack.data_type_leaked or 'veri'
                    }
                    
                    social_posts = self.social_automation.generate_breaking_news_content(post_data)
                    
                    # Sosyal medya içeriklerini kaydet
                    self._save_social_content(social_posts)
                    
                    print(f"[{datetime.now()}] Sosyal medya içeriği oluşturuldu: {critical_attack.company_name}")
            
        except Exception as e:
            print(f"[{datetime.now()}] Sosyal medya içerik oluşturma hatası: {e}")
    
    def _check_critical_attacks(self):
        """Kritik saldırıları kontrol eder"""
        try:
            # Son 1 saatteki kritik saldırıları kontrol et
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=1)
            
            critical_attacks = Post.query.filter(
                Post.discovered >= start_date,
                Post.discovered <= end_date,
                Post.impact_level == 'Kritik'
            ).all()
            
            if critical_attacks:
                print(f"[{datetime.now()}] UYARI: {len(critical_attacks)} kritik saldırı tespit edildi!")
                
                # Kritik saldırıları logla
                self._log_critical_attacks(critical_attacks)
                
                # Acil bildirim gönder (Discord webhook)
                self._send_critical_alert(critical_attacks)
            
        except Exception as e:
            print(f"[{datetime.now()}] Kritik saldırı kontrolü hatası: {e}")
    
    def _update_daily_report(self):
        """Günlük raporu günceller"""
        try:
            # Bugünün raporunu oluştur
            today = datetime.now().date()
            report = self.report_generator.generate_daily_report(today)
            
            # Raporu kaydet
            self.report_generator.save_report(report)
            
            print(f"[{datetime.now()}] Günlük rapor güncellendi: {today}")
            
        except Exception as e:
            print(f"[{datetime.now()}] Günlük rapor güncelleme hatası: {e}")
    
    def _save_social_content(self, social_posts):
        """Sosyal medya içeriklerini kaydeder"""
        try:
            content_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'social_content')
            os.makedirs(content_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for i, post in enumerate(social_posts):
                filename = f"social_post_{timestamp}_{i+1}.json"
                filepath = os.path.join(content_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(post, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"[{datetime.now()}] Sosyal medya içerik kaydetme hatası: {e}")
    
    def _log_critical_attacks(self, attacks):
        """Kritik saldırıları loglar"""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, 'critical_attacks.log')
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now()}] KRİTİK SALDIRI UYARISI\n")
                for attack in attacks:
                    f.write(f"  - Şirket: {attack.company_name or 'Bilinmeyen'}\n")
                    f.write(f"    Sektör: {attack.sector or 'Bilinmeyen'}\n")
                    f.write(f"    Ülke: {attack.country or 'Bilinmeyen'}\n")
                    f.write(f"    Tehdit Aktörü: {attack.name or 'Bilinmeyen'}\n")
                    f.write(f"    Tarih: {attack.created_at}\n")
                    f.write(f"    Risk Seviyesi: {attack.impact_level or 'Bilinmeyen'}\n")
                    f.write(f"    Açıklama: {attack.description or 'Detay yok'}\n")
                    f.write(f"    URL: {attack.post_url or 'Yok'}\n")
                    f.write("-" * 50 + "\n")
            
        except Exception as e:
            print(f"[{datetime.now()}] Kritik saldırı loglama hatası: {e}")
    
    def _send_critical_alert(self, attacks):
        """Kritik saldırı uyarısı gönderir"""
        try:
            # Discord webhook URL'si (config'den alınmalı)
            webhook_url = "YOUR_DISCORD_WEBHOOK_URL"  # Gerçek URL ile değiştirilmeli
            
            if webhook_url == "YOUR_DISCORD_WEBHOOK_URL":
                print(f"[{datetime.now()}] Discord webhook URL'si ayarlanmamış, uyarı gönderilemedi")
                return
            
            import requests
            
            # Uyarı mesajı oluştur
            message = f"🚨 **KRİTİK SALDIRI UYARISI** 🚨\n\n"
            message += f"**{len(attacks)} kritik saldırı tespit edildi!**\n\n"
            
            for i, attack in enumerate(attacks[:3]):  # İlk 3 saldırıyı göster
                message += f"**{i+1}. {attack.company_name or 'Bilinmeyen Şirket'}**\n"
                message += f"   • Sektör: {attack.sector or 'Bilinmeyen'}\n"
                message += f"   • Ülke: {attack.country or 'Bilinmeyen'}\n"
                message += f"   • Tehdit Aktörü: {attack.name or 'Bilinmeyen'}\n"
                message += f"   • Risk: {attack.impact_level or 'Bilinmeyen'}\n\n"
            
            if len(attacks) > 3:
                message += f"... ve {len(attacks) - 3} saldırı daha\n\n"
            
            message += f"**Detaylı rapor:** http://localhost:5000/\n"
            message += f"**Zaman:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Discord'a gönder
            payload = {
                "content": message,
                "username": "CTI-BOT Alert System",
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                print(f"[{datetime.now()}] Kritik saldırı uyarısı Discord'a gönderildi")
            else:
                print(f"[{datetime.now()}] Discord uyarı gönderme hatası: {response.status_code}")
            
        except Exception as e:
            print(f"[{datetime.now()}] Discord uyarı gönderme hatası: {e}")
    
    def get_status(self):
        """Güncelleme durumunu döndürür"""
        return {
            'is_running': self.is_running,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'update_interval': self.update_interval,
            'next_update': (self.last_update + timedelta(seconds=self.update_interval)).isoformat() if self.last_update else None
        }
    
    def force_update(self):
        """Zorla güncelleme yapar"""
        if self.is_running:
            self._perform_update()
            print(f"[{datetime.now()}] Zorla güncelleme tamamlandı")
        else:
            print(f"[{datetime.now()}] Real-time güncellemeler çalışmıyor")
