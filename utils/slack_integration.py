"""
CTI-BOT Slack Integration
Slack webhook entegrasyonu ve bildirim sistemi
"""

import requests
import json
from datetime import datetime, timedelta
from flask import current_app
import os

class SlackIntegration:
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.channel = os.getenv('SLACK_CHANNEL', '#cti-bot')
        self.username = 'CTI-BOT'
        self.icon_emoji = ':shield:'
        self.enabled = bool(self.webhook_url)
    
    def send_message(self, message, channel=None, username=None, icon_emoji=None):
        """Slack'e mesaj gönder"""
        if not self.enabled:
            print("Slack entegrasyonu devre dışı (webhook URL yok)")
            return False
        
        try:
            payload = {
                'text': message,
                'channel': channel or self.channel,
                'username': username or self.username,
                'icon_emoji': icon_emoji or self.icon_emoji
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Slack mesajı başarıyla gönderildi: {message[:50]}...")
                return True
            else:
                print(f"Slack mesaj gönderme hatası: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Slack mesaj gönderme hatası: {e}")
            return False
    
    def send_attack_alert(self, attack_data):
        """Saldırı uyarısı gönder"""
        if not self.enabled:
            return False
        
        try:
            # Mesaj formatı
            message = f"""
🚨 *YENİ SİBER SALDIRI TESPİT EDİLDİ*

*Şirket:* {attack_data.get('company_name', 'Bilinmeyen')}
*Sektör:* {attack_data.get('sector', 'Bilinmeyen')}
*Ülke:* {attack_data.get('country', 'Bilinmeyen')}
*Tehdit Aktörü:* {attack_data.get('threat_actor', 'Bilinmeyen')}
*Etki Seviyesi:* {attack_data.get('impact_level', 'Bilinmeyen')}
*Saldırı Tarihi:* {attack_data.get('hack_date', 'Bilinmeyen')}
*Sızıntıya Uğrayan Veri:* {attack_data.get('data_type_leaked', 'Bilinmeyen')}

*Detaylar:* {attack_data.get('description', 'Detay yok')[:200]}...

*Dashboard:* http://localhost:5000/
*Detay Sayfası:* http://localhost:5000/company-detail?name={attack_data.get('company_name', '').replace(' ', '%20')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Slack saldırı uyarısı hatası: {e}")
            return False
    
    def send_daily_summary(self, summary_data):
        """Günlük özet gönder"""
        if not self.enabled:
            return False
        
        try:
            message = f"""
📊 *CTI-BOT GÜNLÜK ÖZET - {datetime.now().strftime('%d.%m.%Y')}*

*Toplam Saldırı:* {summary_data.get('total_attacks', 0)}
*Benzersiz Şirket:* {summary_data.get('unique_companies', 0)}
*En Çok Hedeflenen Sektör:* {summary_data.get('top_sector', 'Bilinmeyen')}
*En Çok Hedeflenen Ülke:* {summary_data.get('top_country', 'Bilinmeyen')}
*En Aktif Tehdit Aktörü:* {summary_data.get('top_threat_actor', 'Bilinmeyen')}

*Risk Dağılımı:*
• Kritik: {summary_data.get('critical_attacks', 0)}
• Yüksek: {summary_data.get('high_attacks', 0)}
• Orta: {summary_data.get('medium_attacks', 0)}
• Düşük: {summary_data.get('low_attacks', 0)}

*Dashboard:* http://localhost:5000/
*Real-time:* http://localhost:5000/realtime
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Slack günlük özet hatası: {e}")
            return False
    
    def send_weekly_report(self, report_data):
        """Haftalık rapor gönder"""
        if not self.enabled:
            return False
        
        try:
            message = f"""
📈 *CTI-BOT HAFTALIK RAPOR - {report_data.get('week_range', 'Bu Hafta')}*

*Haftalık İstatistikler:*
• Toplam Saldırı: {report_data.get('total_attacks', 0)}
• Yeni Şirket: {report_data.get('new_companies', 0)}
• En Riskli Sektör: {report_data.get('top_sector', 'Bilinmeyen')}
• En Riskli Ülke: {report_data.get('top_country', 'Bilinmeyen')}

*Trend Analizi:*
• Önceki haftaya göre: {report_data.get('trend_change', '0%')}
• En çok artan sektör: {report_data.get('trending_sector', 'Bilinmeyen')}
• En çok artan ülke: {report_data.get('trending_country', 'Bilinmeyen')}

*Detaylı Rapor:* {report_data.get('report_url', 'http://localhost:5000/')}
            """.strip()
            
            return self.send_message(message)
            
        except Exception as e:
            print(f"Slack haftalık rapor hatası: {e}")
            return False
    
    def send_system_alert(self, alert_type, message, severity='info'):
        """Sistem uyarısı gönder"""
        if not self.enabled:
            return False
        
        try:
            # Severity emojileri
            severity_emojis = {
                'info': ':information_source:',
                'warning': ':warning:',
                'error': ':x:',
                'critical': ':rotating_light:'
            }
            
            emoji = severity_emojis.get(severity, ':information_source:')
            
            formatted_message = f"""
{emoji} *SİSTEM UYARISI - {alert_type.upper()}*

*Severity:* {severity.upper()}
*Zaman:* {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
*Mesaj:* {message}

*Dashboard:* http://localhost:5000/
            """.strip()
            
            return self.send_message(formatted_message)
            
        except Exception as e:
            print(f"Slack sistem uyarısı hatası: {e}")
            return False
    
    def send_custom_message(self, title, content, fields=None, color='good'):
        """Özel mesaj gönder (rich format)"""
        if not self.enabled:
            return False
        
        try:
            # Slack attachment oluştur
            attachment = {
                'color': color,
                'title': title,
                'text': content,
                'footer': 'CTI-BOT | Siber Tehdit İstihbarat Platformu',
                'ts': int(datetime.now().timestamp())
            }
            
            if fields:
                attachment['fields'] = fields
            
            payload = {
                'channel': self.channel,
                'username': self.username,
                'icon_emoji': self.icon_emoji,
                'attachments': [attachment]
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Slack özel mesajı başarıyla gönderildi: {title}")
                return True
            else:
                print(f"Slack özel mesaj hatası: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Slack özel mesaj hatası: {e}")
            return False
    
    def test_connection(self):
        """Slack bağlantısını test et"""
        if not self.enabled:
            return {
                'status': 'disabled',
                'message': 'Slack webhook URL ayarlanmamış'
            }
        
        try:
            test_message = f"🧪 CTI-BOT Slack entegrasyonu test mesajı - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            success = self.send_message(test_message)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Slack bağlantısı başarılı'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Slack mesaj gönderilemedi'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Slack test hatası: {e}'
            }

# Global Slack integration instance
slack_integration = SlackIntegration()

