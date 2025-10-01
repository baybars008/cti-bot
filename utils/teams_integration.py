"""
CTI-BOT Microsoft Teams Integration
Teams webhook entegrasyonu ve bildirim sistemi
"""

import requests
import json
from datetime import datetime, timedelta
import os

class TeamsIntegration:
    def __init__(self):
        self.webhook_url = os.getenv('TEAMS_WEBHOOK_URL', '')
        self.enabled = bool(self.webhook_url)
    
    def send_message(self, message, title=None, color='0078D4'):
        """Teams'e mesaj gönder"""
        if not self.enabled:
            print("Teams entegrasyonu devre dışı (webhook URL yok)")
            return False
        
        try:
            # Teams message card formatı
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color,
                "summary": title or "CTI-BOT Bildirimi",
                "sections": [{
                    "activityTitle": title or "CTI-BOT Bildirimi",
                    "activitySubtitle": f"CTI-BOT | {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                    "activityImage": "https://img.icons8.com/color/48/000000/shield.png",
                    "text": message,
                    "markdown": True
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Teams mesajı başarıyla gönderildi: {title or 'Bildirim'}")
                return True
            else:
                print(f"Teams mesaj gönderme hatası: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Teams mesaj gönderme hatası: {e}")
            return False
    
    def send_attack_alert(self, attack_data):
        """Saldırı uyarısı gönder"""
        if not self.enabled:
            return False
        
        try:
            # Risk seviyesine göre renk belirle
            risk_colors = {
                'Kritik': 'DC3545',
                'Yüksek': 'FD7E14',
                'Orta': 'FFC107',
                'Düşük': '28A745'
            }
            
            impact_level = attack_data.get('impact_level', 'Orta')
            color = risk_colors.get(impact_level, '0078D4')
            
            title = f"🚨 YENİ SİBER SALDIRI: {attack_data.get('company_name', 'Bilinmeyen Şirket')}"
            
            message = f"""
**Şirket:** {attack_data.get('company_name', 'Bilinmeyen')}
**Sektör:** {attack_data.get('sector', 'Bilinmeyen')}
**Ülke:** {attack_data.get('country', 'Bilinmeyen')}
**Tehdit Aktörü:** {attack_data.get('threat_actor', 'Bilinmeyen')}
**Etki Seviyesi:** {impact_level}
**Saldırı Tarihi:** {attack_data.get('hack_date', 'Bilinmeyen')}
**Sızıntıya Uğrayan Veri:** {attack_data.get('data_type_leaked', 'Bilinmeyen')}

**Açıklama:**
{attack_data.get('description', 'Detay yok')[:300]}...

**Bağlantılar:**
• [Dashboard](http://localhost:5000/)
• [Detay Sayfası](http://localhost:5000/company-detail?name={attack_data.get('company_name', '').replace(' ', '%20')})
            """.strip()
            
            return self.send_message(message, title, color)
            
        except Exception as e:
            print(f"Teams saldırı uyarısı hatası: {e}")
            return False
    
    def send_daily_summary(self, summary_data):
        """Günlük özet gönder"""
        if not self.enabled:
            return False
        
        try:
            title = f"📊 CTI-BOT Günlük Özet - {datetime.now().strftime('%d.%m.%Y')}"
            
            message = f"""
**İSTATİSTİKLER:**
• **Toplam Saldırı:** {summary_data.get('total_attacks', 0)}
• **Benzersiz Şirket:** {summary_data.get('unique_companies', 0)}
• **En Çok Hedeflenen Sektör:** {summary_data.get('top_sector', 'Bilinmeyen')}
• **En Çok Hedeflenen Ülke:** {summary_data.get('top_country', 'Bilinmeyen')}
• **En Aktif Tehdit Aktörü:** {summary_data.get('top_threat_actor', 'Bilinmeyen')}

**RİSK DAĞILIMI:**
• 🔴 **Kritik:** {summary_data.get('critical_attacks', 0)}
• 🟠 **Yüksek:** {summary_data.get('high_attacks', 0)}
• 🟡 **Orta:** {summary_data.get('medium_attacks', 0)}
• 🟢 **Düşük:** {summary_data.get('low_attacks', 0)}

**Bağlantılar:**
• [Dashboard](http://localhost:5000/)
• [Real-time Görünüm](http://localhost:5000/realtime)
            """.strip()
            
            return self.send_message(message, title, '0078D4')
            
        except Exception as e:
            print(f"Teams günlük özet hatası: {e}")
            return False
    
    def send_weekly_report(self, report_data):
        """Haftalık rapor gönder"""
        if not self.enabled:
            return False
        
        try:
            title = f"📈 CTI-BOT Haftalık Rapor - {report_data.get('week_range', 'Bu Hafta')}"
            
            message = f"""
**HAFTALIK İSTATİSTİKLER:**
• **Toplam Saldırı:** {report_data.get('total_attacks', 0)}
• **Yeni Şirket:** {report_data.get('new_companies', 0)}
• **En Riskli Sektör:** {report_data.get('top_sector', 'Bilinmeyen')}
• **En Riskli Ülke:** {report_data.get('top_country', 'Bilinmeyen')}

**TREND ANALİZİ:**
• **Önceki haftaya göre:** {report_data.get('trend_change', '0%')}
• **En çok artan sektör:** {report_data.get('trending_sector', 'Bilinmeyen')}
• **En çok artan ülke:** {report_data.get('trending_country', 'Bilinmeyen')}

**Detaylı Rapor:** [Raporu Görüntüle]({report_data.get('report_url', 'http://localhost:5000/')})
            """.strip()
            
            return self.send_message(message, title, '28A745')
            
        except Exception as e:
            print(f"Teams haftalık rapor hatası: {e}")
            return False
    
    def send_system_alert(self, alert_type, message, severity='info'):
        """Sistem uyarısı gönder"""
        if not self.enabled:
            return False
        
        try:
            # Severity renkleri
            severity_colors = {
                'info': '0078D4',
                'warning': 'FFC107',
                'error': 'DC3545',
                'critical': '6F42C1'
            }
            
            # Severity emojileri
            severity_emojis = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'error': '❌',
                'critical': '🚨'
            }
            
            emoji = severity_emojis.get(severity, 'ℹ️')
            color = severity_colors.get(severity, '0078D4')
            
            title = f"{emoji} SİSTEM UYARISI - {alert_type.upper()}"
            
            formatted_message = f"""
**Severity:** {severity.upper()}
**Zaman:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
**Mesaj:** {message}

**Dashboard:** [CTI-BOT Dashboard](http://localhost:5000/)
            """.strip()
            
            return self.send_message(formatted_message, title, color)
            
        except Exception as e:
            print(f"Teams sistem uyarısı hatası: {e}")
            return False
    
    def send_rich_message(self, title, content, facts=None, actions=None, color='0078D4'):
        """Zengin formatlı mesaj gönder"""
        if not self.enabled:
            return False
        
        try:
            # Facts (key-value pairs) oluştur
            facts_list = []
            if facts:
                for key, value in facts.items():
                    facts_list.append({
                        "name": key,
                        "value": str(value)
                    })
            
            # Actions (buttons) oluştur
            actions_list = []
            if actions:
                for action in actions:
                    actions_list.append({
                        "@type": "OpenUri",
                        "name": action.get('name', 'Bağlantı'),
                        "targets": [{
                            "os": "default",
                            "uri": action.get('url', 'http://localhost:5000/')
                        }]
                    })
            
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color,
                "summary": title,
                "sections": [{
                    "activityTitle": title,
                    "activitySubtitle": f"CTI-BOT | {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                    "activityImage": "https://img.icons8.com/color/48/000000/shield.png",
                    "text": content,
                    "facts": facts_list,
                    "markdown": True
                }],
                "potentialAction": actions_list
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Teams zengin mesajı başarıyla gönderildi: {title}")
                return True
            else:
                print(f"Teams zengin mesaj hatası: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Teams zengin mesaj hatası: {e}")
            return False
    
    def test_connection(self):
        """Teams bağlantısını test et"""
        if not self.enabled:
            return {
                'status': 'disabled',
                'message': 'Teams webhook URL ayarlanmamış'
            }
        
        try:
            test_title = f"🧪 CTI-BOT Teams Test - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            test_message = "Bu bir test mesajıdır. CTI-BOT Teams entegrasyonu çalışıyor."
            
            success = self.send_message(test_message, test_title)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Teams bağlantısı başarılı'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Teams mesaj gönderilemedi'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Teams test hatası: {e}'
            }

# Global Teams integration instance
teams_integration = TeamsIntegration()

