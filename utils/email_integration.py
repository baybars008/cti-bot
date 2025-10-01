"""
CTI-BOT Email Integration
Email bildirim sistemi ve rapor gönderimi
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import os
import json

class EmailIntegration:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.sender_name = os.getenv('SENDER_NAME', 'CTI-BOT')
        self.enabled = bool(self.sender_email and self.sender_password)
    
    def send_email(self, to_emails, subject, body, html_body=None, attachments=None):
        """Email gönder"""
        if not self.enabled:
            print("Email entegrasyonu devre dışı (SMTP ayarları yok)")
            return False
        
        try:
            # Email mesajı oluştur
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
            message['Subject'] = subject
            
            # Text ve HTML body ekle
            text_part = MIMEText(body, 'plain', 'utf-8')
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                message.attach(html_part)
            
            # Ek dosyalar ekle
            if attachments:
                for attachment in attachments:
                    with open(attachment['file_path'], 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {attachment["filename"]}'
                        )
                        message.attach(part)
            
            # SMTP bağlantısı ve gönderim
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"Email başarıyla gönderildi: {subject}")
            return True
            
        except Exception as e:
            print(f"Email gönderme hatası: {e}")
            return False
    
    def send_attack_alert(self, to_emails, attack_data):
        """Saldırı uyarısı email'i gönder"""
        if not self.enabled:
            return False
        
        try:
            subject = f"🚨 YENİ SİBER SALDIRI: {attack_data.get('company_name', 'Bilinmeyen Şirket')}"
            
            # Text body
            text_body = f"""
CTI-BOT SİBER SALDIRI UYARISI

Yeni bir siber saldırı tespit edildi:

Şirket: {attack_data.get('company_name', 'Bilinmeyen')}
Sektör: {attack_data.get('sector', 'Bilinmeyen')}
Ülke: {attack_data.get('country', 'Bilinmeyen')}
Tehdit Aktörü: {attack_data.get('threat_actor', 'Bilinmeyen')}
Etki Seviyesi: {attack_data.get('impact_level', 'Bilinmeyen')}
Saldırı Tarihi: {attack_data.get('hack_date', 'Bilinmeyen')}
Sızıntıya Uğrayan Veri: {attack_data.get('data_type_leaked', 'Bilinmeyen')}

Açıklama:
{attack_data.get('description', 'Detay yok')}

Dashboard: http://localhost:5000/
Detay Sayfası: http://localhost:5000/company-detail?name={attack_data.get('company_name', '').replace(' ', '%20')}

---
CTI-BOT | Siber Tehdit İstihbarat Platformu
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CTI-BOT Saldırı Uyarısı</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #dc3545; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .alert {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        .info-table th, .info-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        .info-table th {{ background-color: #f8f9fa; font-weight: bold; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 YENİ SİBER SALDIRI TESPİT EDİLDİ</h1>
        </div>
        
        <div class="alert">
            <strong>Uyarı:</strong> {attack_data.get('company_name', 'Bilinmeyen')} şirketine yönelik yeni bir siber saldırı tespit edildi.
        </div>
        
        <table class="info-table">
            <tr><th>Şirket</th><td>{attack_data.get('company_name', 'Bilinmeyen')}</td></tr>
            <tr><th>Sektör</th><td>{attack_data.get('sector', 'Bilinmeyen')}</td></tr>
            <tr><th>Ülke</th><td>{attack_data.get('country', 'Bilinmeyen')}</td></tr>
            <tr><th>Tehdit Aktörü</th><td>{attack_data.get('threat_actor', 'Bilinmeyen')}</td></tr>
            <tr><th>Etki Seviyesi</th><td>{attack_data.get('impact_level', 'Bilinmeyen')}</td></tr>
            <tr><th>Saldırı Tarihi</th><td>{attack_data.get('hack_date', 'Bilinmeyen')}</td></tr>
            <tr><th>Sızıntıya Uğrayan Veri</th><td>{attack_data.get('data_type_leaked', 'Bilinmeyen')}</td></tr>
        </table>
        
        <h3>Açıklama:</h3>
        <p>{attack_data.get('description', 'Detay yok')}</p>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="http://localhost:5000/" class="btn">Dashboard'ı Görüntüle</a>
            <a href="http://localhost:5000/company-detail?name={attack_data.get('company_name', '').replace(' ', '%20')}" class="btn">Detay Sayfası</a>
        </div>
        
        <div class="footer">
            <p>CTI-BOT | Siber Tehdit İstihbarat Platformu</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_emails, subject, text_body, html_body)
            
        except Exception as e:
            print(f"Email saldırı uyarısı hatası: {e}")
            return False
    
    def send_daily_summary(self, to_emails, summary_data):
        """Günlük özet email'i gönder"""
        if not self.enabled:
            return False
        
        try:
            subject = f"📊 CTI-BOT Günlük Özet - {datetime.now().strftime('%d.%m.%Y')}"
            
            # Text body
            text_body = f"""
CTI-BOT GÜNLÜK ÖZET - {datetime.now().strftime('%d.%m.%Y')}

İSTATİSTİKLER:
• Toplam Saldırı: {summary_data.get('total_attacks', 0)}
• Benzersiz Şirket: {summary_data.get('unique_companies', 0)}
• En Çok Hedeflenen Sektör: {summary_data.get('top_sector', 'Bilinmeyen')}
• En Çok Hedeflenen Ülke: {summary_data.get('top_country', 'Bilinmeyen')}
• En Aktif Tehdit Aktörü: {summary_data.get('top_threat_actor', 'Bilinmeyen')}

RİSK DAĞILIMI:
• Kritik: {summary_data.get('critical_attacks', 0)}
• Yüksek: {summary_data.get('high_attacks', 0)}
• Orta: {summary_data.get('medium_attacks', 0)}
• Düşük: {summary_data.get('low_attacks', 0)}

Dashboard: http://localhost:5000/
Real-time: http://localhost:5000/realtime

---
CTI-BOT | Siber Tehdit İstihbarat Platformu
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CTI-BOT Günlük Özet</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #007bff; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .risk-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }}
        .risk-card {{ padding: 10px; border-radius: 5px; text-align: center; color: white; }}
        .risk-critical {{ background-color: #dc3545; }}
        .risk-high {{ background-color: #fd7e14; }}
        .risk-medium {{ background-color: #ffc107; color: #000; }}
        .risk-low {{ background-color: #28a745; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 CTI-BOT Günlük Özet</h1>
            <p>{datetime.now().strftime('%d.%m.%Y')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{summary_data.get('total_attacks', 0)}</div>
                <div class="stat-label">Toplam Saldırı</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary_data.get('unique_companies', 0)}</div>
                <div class="stat-label">Benzersiz Şirket</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary_data.get('top_sector', 'N/A')}</div>
                <div class="stat-label">En Riskli Sektör</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary_data.get('top_country', 'N/A')}</div>
                <div class="stat-label">En Riskli Ülke</div>
            </div>
        </div>
        
        <h3>Risk Dağılımı:</h3>
        <div class="risk-grid">
            <div class="risk-card risk-critical">
                <div style="font-size: 18px; font-weight: bold;">{summary_data.get('critical_attacks', 0)}</div>
                <div>Kritik</div>
            </div>
            <div class="risk-card risk-high">
                <div style="font-size: 18px; font-weight: bold;">{summary_data.get('high_attacks', 0)}</div>
                <div>Yüksek</div>
            </div>
            <div class="risk-card risk-medium">
                <div style="font-size: 18px; font-weight: bold;">{summary_data.get('medium_attacks', 0)}</div>
                <div>Orta</div>
            </div>
            <div class="risk-card risk-low">
                <div style="font-size: 18px; font-weight: bold;">{summary_data.get('low_attacks', 0)}</div>
                <div>Düşük</div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 20px 0;">
            <a href="http://localhost:5000/" class="btn">Dashboard'ı Görüntüle</a>
            <a href="http://localhost:5000/realtime" class="btn">Real-time Görünüm</a>
        </div>
        
        <div class="footer">
            <p>CTI-BOT | Siber Tehdit İstihbarat Platformu</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(to_emails, subject, text_body, html_body)
            
        except Exception as e:
            print(f"Email günlük özet hatası: {e}")
            return False
    
    def send_weekly_report(self, to_emails, report_data, report_file_path=None):
        """Haftalık rapor email'i gönder"""
        if not self.enabled:
            return False
        
        try:
            subject = f"📈 CTI-BOT Haftalık Rapor - {report_data.get('week_range', 'Bu Hafta')}"
            
            # Text body
            text_body = f"""
CTI-BOT HAFTALIK RAPOR - {report_data.get('week_range', 'Bu Hafta')}

HAFTALIK İSTATİSTİKLER:
• Toplam Saldırı: {report_data.get('total_attacks', 0)}
• Yeni Şirket: {report_data.get('new_companies', 0)}
• En Riskli Sektör: {report_data.get('top_sector', 'Bilinmeyen')}
• En Riskli Ülke: {report_data.get('top_country', 'Bilinmeyen')}

TREND ANALİZİ:
• Önceki haftaya göre: {report_data.get('trend_change', '0%')}
• En çok artan sektör: {report_data.get('trending_sector', 'Bilinmeyen')}
• En çok artan ülke: {report_data.get('trending_country', 'Bilinmeyen')}

Detaylı Rapor: {report_data.get('report_url', 'http://localhost:5000/')}

---
CTI-BOT | Siber Tehdit İstihbarat Platformu
            """.strip()
            
            # Attachments
            attachments = []
            if report_file_path and os.path.exists(report_file_path):
                attachments.append({
                    'file_path': report_file_path,
                    'filename': f"cti_bot_weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
                })
            
            return self.send_email(to_emails, subject, text_body, attachments=attachments)
            
        except Exception as e:
            print(f"Email haftalık rapor hatası: {e}")
            return False
    
    def test_connection(self):
        """Email bağlantısını test et"""
        if not self.enabled:
            return {
                'status': 'disabled',
                'message': 'Email SMTP ayarları yapılmamış'
            }
        
        try:
            test_subject = f"🧪 CTI-BOT Email Test - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            test_body = "Bu bir test email'idir. CTI-BOT email entegrasyonu çalışıyor."
            
            # Test email'i kendine gönder
            success = self.send_email([self.sender_email], test_subject, test_body)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Email bağlantısı başarılı'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Email gönderilemedi'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Email test hatası: {e}'
            }

# Global email integration instance
email_integration = EmailIntegration()

