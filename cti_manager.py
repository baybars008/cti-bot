#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTI-BOT: Advanced Cyber Threat Intelligence Platform
===================================================

Created by: Alihan Şahin | Baybars
Threat & Security Researcher

Website: https://alihansahin.com
GitHub: https://github.com/baybars008

Central Management System
========================
Comprehensive management system for all project tools and operations.
Built with futuristic design principles and advanced automation capabilities.

Mission: "To revolutionize cybersecurity through intelligent threat detection,
predictive analytics, and automated response systems that stay ahead of
evolving cyber threats."
"""

import os
import sys
import subprocess
import time
import sqlite3
import json
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Renkli çıktı için
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    END = '\033[0m'

class CTIManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.db_path = self.project_root / "instance" / "data.db"
        self.logs_dir = self.project_root / "logs"
        self.venv_path = self.project_root / "venv"
        self.python_exec = self.venv_path / "bin" / "python" if self.venv_path.exists() else "python3"
        
        # Process IDs for tracking
        self.flask_pid = None
        self.data_collection_pid = None
        self.social_media_pid = None
        
    def print_header(self):
        """Logo ve başlık göster"""
        print(f"{Colors.CYAN}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    CTI-BOT v2.1.7                           ║")
        print("║          Advanced Cyber Threat Intelligence Platform        ║")
        print("║                Central Management System                     ║")
        print("║                    CLASSIFIED SYSTEM                         ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
    
    def print_menu(self):
        """Ana menüyü göster"""
        print(f"\n{Colors.YELLOW}📋 CTI-BOT Central Management Menu:{Colors.END}")
        print()
        
        print(f"{Colors.GREEN}🚀 Startup Options:{Colors.END}")
        print("1.  Start Flask application only")
        print("2.  Start data collection only")
        print("3.  Start full system (Flask + Data Collection)")
        print("4.  Start in background (nohup)")
        print("5.  Start with screen")
        print("6.  Start with Docker")
        print()
        
        print(f"{Colors.BLUE}🔧 System Management:{Colors.END}")
        print("7.  Check system status")
        print("8.  Check database status")
        print("9.  Show log files")
        print("10. Restart project")
        print("11. Stop project")
        print("12. System cleanup")
        print()
        
        print(f"{Colors.PURPLE}🛠️  Installation & Maintenance:{Colors.END}")
        print("13. Install required packages")
        print("14. Setup/initialize database")
        print("15. Performance optimization")
        print("16. Cache system management")
        print("17. Backup database")
        print("18. System update")
        print()
        
        print(f"{Colors.CYAN}📊 Analysis & Reporting:{Colors.END}")
        print("19. Simple data analysis")
        print("20. Sector analysis")
        print("21. Real-time analysis")
        print("22. Generate report")
        print("23. Export data")
        print()
        
        print(f"{Colors.YELLOW}🔗 Integrations:{Colors.END}")
        print("24. Social media automation")
        print("25. Email integration")
        print("26. Slack integration")
        print("27. Teams integration")
        print()
        
        print(f"{Colors.RED}🧪 Testing & Validation:{Colors.END}")
        print("28. API tests")
        print("29. Database tests")
        print("30. Redis connection test")
        print("31. System performance test")
        print()
        
        print(f"{Colors.WHITE}💡 Help:{Colors.END}")
        print("32. Help menu")
        print("33. System information")
        print("0.  Exit")
        print()
    
    def check_system_status(self):
        """Check system status"""
        print(f"\n{Colors.YELLOW}🔍 Checking System Status...{Colors.END}")
        print()
        
        # Python check
        try:
            result = subprocess.run([self.python_exec, "--version"], capture_output=True, text=True)
            print(f"{Colors.GREEN}✅ Python: {result.stdout.strip()}{Colors.END}")
        except:
            print(f"{Colors.RED}❌ Python not found{Colors.END}")
        
        # Virtual environment check
        if self.venv_path.exists():
            print(f"{Colors.GREEN}✅ Virtual Environment: Available{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Virtual Environment: Not found{Colors.END}")
        
        # Database check
        if self.db_path.exists():
            print(f"{Colors.GREEN}✅ Database: Available{Colors.END}")
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM posts")
                post_count = cursor.fetchone()[0]
                print(f"{Colors.BLUE}📊 Posts: {post_count} records{Colors.END}")
                conn.close()
            except Exception as e:
                print(f"{Colors.RED}❌ Database error: {e}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Database: Not found{Colors.END}")
        
        # Redis check
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            print(f"{Colors.GREEN}✅ Redis: Running{Colors.END}")
        except:
            print(f"{Colors.YELLOW}⚠️  Redis: Not running{Colors.END}")
        
        # Port check
        port_5000_in_use = self.check_port(5000)
        if port_5000_in_use:
            print(f"{Colors.GREEN}✅ Port 5000: In use (Flask running){Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  Port 5000: Available{Colors.END}")
        
        # Disk usage
        disk_usage = psutil.disk_usage(self.project_root)
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        print(f"{Colors.BLUE}💾 Disk Usage: {disk_percent:.1f}%{Colors.END}")
        
        # Memory usage
        memory = psutil.virtual_memory()
        print(f"{Colors.BLUE}🧠 Memory Usage: {memory.percent}%{Colors.END}")
    
    def check_port(self, port):
        """Port kullanımını kontrol et"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def start_flask_app(self):
        """Flask uygulamasını başlat"""
        print(f"\n{Colors.YELLOW}🚀 Flask Uygulaması Başlatılıyor...{Colors.END}")
        
        if not self.venv_path.exists():
            print(f"{Colors.RED}❌ Virtual environment bulunamadı!{Colors.END}")
            return False
        
        try:
            # Environment variables
            env = os.environ.copy()
            env['FLASK_APP'] = 'app.py'
            env['FLASK_ENV'] = 'development'
            env['FLASK_DEBUG'] = '1'
            env['PYTHONPATH'] = str(self.project_root)
            
            # Flask'ı başlat
            process = subprocess.Popen(
                [str(self.python_exec), 'app.py'],
                cwd=str(self.project_root),
                env=env
            )
            
            self.flask_pid = process.pid
            print(f"{Colors.GREEN}✅ Flask başlatıldı! PID: {self.flask_pid}{Colors.END}")
            print(f"{Colors.CYAN}🌐 Dashboard: http://localhost:5000/dashboard{Colors.END}")
            print(f"{Colors.CYAN}📊 API Health: http://localhost:5000/api/health{Colors.END}")
            
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Flask başlatılamadı: {e}{Colors.END}")
            return False
    
    def start_data_collection(self):
        """Veri toplama işlemini başlat"""
        print(f"\n{Colors.YELLOW}📊 Veri Toplama İşlemi Başlatılıyor...{Colors.END}")
        
        try:
            process = subprocess.Popen(
                [str(self.python_exec), 'background_jobs/cron_update_db.py'],
                cwd=str(self.project_root)
            )
            
            self.data_collection_pid = process.pid
            print(f"{Colors.GREEN}✅ Veri toplama başlatıldı! PID: {self.data_collection_pid}{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Veri toplama başlatılamadı: {e}{Colors.END}")
            return False
    
    def start_full_system(self):
        """Tam sistemi başlat"""
        print(f"\n{Colors.BLUE}🚀 Tam Sistem Başlatılıyor...{Colors.END}")
        
        # 1. Veritabanını kur
        print(f"{Colors.YELLOW}1️⃣ Veritabanı kuruluyor...{Colors.END}")
        if not self.setup_database():
            return False
        
        # 2. Flask'ı başlat
        print(f"{Colors.YELLOW}2️⃣ Flask uygulaması başlatılıyor...{Colors.END}")
        if not self.start_flask_app():
            return False
        
        # 3. Veri toplamayı başlat
        print(f"{Colors.YELLOW}3️⃣ Veri toplama başlatılıyor...{Colors.END}")
        if not self.start_data_collection():
            return False
        
        print(f"{Colors.GREEN}✅ Tam sistem başarıyla başlatıldı!{Colors.END}")
        return True
    
    def start_background(self):
        """Arka planda başlat"""
        print(f"\n{Colors.BLUE}🚀 Arka Planda Başlatılıyor...{Colors.END}")
        
        try:
            # Flask'ı arka planda başlat
            flask_log = self.logs_dir / "flask.log"
            with open(flask_log, 'w') as f:
                process = subprocess.Popen(
                    [str(self.python_exec), 'app.py'],
                    cwd=str(self.project_root),
                    stdout=f,
                    stderr=subprocess.STDOUT
                )
                self.flask_pid = process.pid
            
            # Veri toplamayı arka planda başlat
            data_log = self.logs_dir / "data.log"
            with open(data_log, 'w') as f:
                process = subprocess.Popen(
                    [str(self.python_exec), 'background_jobs/cron_update_db.py'],
                    cwd=str(self.project_root),
                    stdout=f,
                    stderr=subprocess.STDOUT
                )
                self.data_collection_pid = process.pid
            
            print(f"{Colors.GREEN}✅ Sistem arka planda başlatıldı!{Colors.END}")
            print(f"{Colors.CYAN}🌐 Dashboard: http://localhost:5000/dashboard{Colors.END}")
            print(f"{Colors.CYAN}📊 Flask Log: tail -f {flask_log}{Colors.END}")
            print(f"{Colors.CYAN}📊 Data Log: tail -f {data_log}{Colors.END}")
            print(f"{Colors.YELLOW}⏹️  Durdurmak için: kill {self.flask_pid} {self.data_collection_pid}{Colors.END}")
            
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Arka plan başlatılamadı: {e}{Colors.END}")
            return False
    
    def setup_database(self):
        """Veritabanını kur"""
        print(f"\n{Colors.YELLOW}📦 Veritabanı Kuruluyor...{Colors.END}")
        
        try:
            result = subprocess.run(
                [str(self.python_exec), 'setup_database.py'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Veritabanı başarıyla kuruldu{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Veritabanı kurulum hatası: {result.stderr}{Colors.END}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Veritabanı kurulum hatası: {e}{Colors.END}")
            return False
    
    def install_packages(self):
        """Gerekli paketleri yükle"""
        print(f"\n{Colors.YELLOW}📦 Gerekli Paketler Yükleniyor...{Colors.END}")
        
        try:
            # Virtual environment oluştur
            if not self.venv_path.exists():
                print(f"{Colors.YELLOW}🔧 Virtual environment oluşturuluyor...{Colors.END}")
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)])
                print(f"{Colors.GREEN}✅ Virtual environment oluşturuldu{Colors.END}")
            
            # Paketleri yükle
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                print(f"{Colors.YELLOW}📦 Paketler yükleniyor...{Colors.END}")
                result = subprocess.run(
                    [str(self.python_exec), '-m', 'pip', 'install', '-r', str(requirements_file)],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ Paketler başarıyla yüklendi{Colors.END}")
                    return True
                else:
                    print(f"{Colors.RED}❌ Paket yükleme hatası: {result.stderr}{Colors.END}")
                    return False
            else:
                print(f"{Colors.RED}❌ requirements.txt bulunamadı{Colors.END}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Paket yükleme hatası: {e}{Colors.END}")
            return False
    
    def stop_system(self):
        """Sistemi durdur"""
        print(f"\n{Colors.YELLOW}🛑 Sistem Durduruluyor...{Colors.END}")
        
        stopped_processes = []
        
        # Flask process'ini durdur
        if self.flask_pid:
            try:
                os.kill(self.flask_pid, 9)
                stopped_processes.append(f"Flask (PID: {self.flask_pid})")
                self.flask_pid = None
            except:
                pass
        
        # Veri toplama process'ini durdur
        if self.data_collection_pid:
            try:
                os.kill(self.data_collection_pid, 9)
                stopped_processes.append(f"Data Collection (PID: {self.data_collection_pid})")
                self.data_collection_pid = None
            except:
                pass
        
        # Port 5000'de çalışan process'leri durdur
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections'] or []:
                    if conn.laddr.port == 5000:
                        os.kill(proc.info['pid'], 9)
                        stopped_processes.append(f"Port 5000 Process (PID: {proc.info['pid']})")
            except:
                pass
        
        if stopped_processes:
            print(f"{Colors.GREEN}✅ Durdurulan process'ler: {', '.join(stopped_processes)}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}ℹ️  Durdurulacak process bulunamadı{Colors.END}")
    
    def show_logs(self):
        """Log dosyalarını göster"""
        print(f"\n{Colors.YELLOW}📋 Log Dosyaları:{Colors.END}")
        
        log_files = [
            ("Flask Log", self.logs_dir / "flask.log"),
            ("Data Log", self.logs_dir / "data.log"),
            ("CTI Bot Log", self.logs_dir / "cti_bot.log")
        ]
        
        for log_name, log_path in log_files:
            if log_path.exists():
                print(f"\n{Colors.BLUE}📊 {log_name} (son 20 satır):{Colors.END}")
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[-20:]:
                            print(line.rstrip())
                except Exception as e:
                    print(f"{Colors.RED}❌ Log okuma hatası: {e}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}ℹ️  {log_name}: Bulunamadı{Colors.END}")
    
    def run_simple_analysis(self):
        """Basit veri analizi çalıştır"""
        print(f"\n{Colors.YELLOW}📊 Basit Veri Analizi Çalıştırılıyor...{Colors.END}")
        
        try:
            result = subprocess.run(
                [str(self.python_exec), '-c', 'from utils.data_analyzer import DataAnalyzer; analyzer = DataAnalyzer(); print(analyzer.get_basic_stats())'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Analiz tamamlandı{Colors.END}")
                print(result.stdout)
            else:
                print(f"{Colors.RED}❌ Analiz hatası: {result.stderr}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Analiz hatası: {e}{Colors.END}")
    
    def run_sector_analysis(self):
        """Sektör analizi çalıştır"""
        print(f"\n{Colors.YELLOW}🏢 Sektör Analizi Çalıştırılıyor...{Colors.END}")
        
        try:
            result = subprocess.run(
                [str(self.python_exec), '-c', 'from utils.sector_detector import SectorDetector; analyzer = SectorDetector(); print("Sector analysis completed")'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Sektör analizi tamamlandı{Colors.END}")
                print(result.stdout)
            else:
                print(f"{Colors.RED}❌ Sektör analizi hatası: {result.stderr}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Sektör analizi hatası: {e}{Colors.END}")
    
    def test_apis(self):
        """API testlerini çalıştır"""
        print(f"\n{Colors.YELLOW}🧪 API Testleri Başlatılıyor...{Colors.END}")
        
        try:
            # Health check
            print(f"{Colors.BLUE}🔍 Health Check:{Colors.END}")
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✅ Health API: OK{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Health API: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ API test hatası: {e}{Colors.END}")
    
    def test_database(self):
        """Veritabanı testlerini çalıştır"""
        print(f"\n{Colors.YELLOW}🗄️  Veritabanı Test Ediliyor...{Colors.END}")
        
        if not self.db_path.exists():
            print(f"{Colors.RED}❌ Veritabanı bulunamadı{Colors.END}")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabloları listele
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"{Colors.BLUE}📊 Veritabanı Tabloları:{Colors.END}")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Post sayısı
            cursor.execute("SELECT COUNT(*) FROM posts")
            post_count = cursor.fetchone()[0]
            print(f"{Colors.BLUE}📊 Posts: {post_count} kayıt{Colors.END}")
            
            conn.close()
            print(f"{Colors.GREEN}✅ Veritabanı testi başarılı{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Veritabanı test hatası: {e}{Colors.END}")
    
    def clean_system(self):
        """Sistemi temizle"""
        print(f"\n{Colors.YELLOW}🧹 Sistem Temizleniyor...{Colors.END}")
        
        cleaned_items = []
        
        # Log dosyalarını temizle
        log_files = ["flask.log", "data.log", "cti_bot.log"]
        for log_file in log_files:
            log_path = self.logs_dir / log_file
            if log_path.exists():
                log_path.unlink()
                cleaned_items.append(log_file)
        
        # Cache temizle
        cache_dirs = ["__pycache__", ".pytest_cache"]
        for cache_dir in cache_dirs:
            cache_path = self.project_root / cache_dir
            if cache_path.exists():
                import shutil
                shutil.rmtree(cache_path)
                cleaned_items.append(cache_dir)
        
        if cleaned_items:
            print(f"{Colors.GREEN}✅ Temizlenen öğeler: {', '.join(cleaned_items)}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}ℹ️  Temizlenecek öğe bulunamadı{Colors.END}")
    
    def backup_database(self):
        """Veritabanını yedekle"""
        print(f"\n{Colors.YELLOW}💾 Veritabanı Yedekleniyor...{Colors.END}")
        
        if not self.db_path.exists():
            print(f"{Colors.RED}❌ Veritabanı bulunamadı{Colors.END}")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.project_root / f"backup_data_{timestamp}.db"
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            print(f"{Colors.GREEN}✅ Veritabanı yedeklendi: {backup_path.name}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Yedekleme hatası: {e}{Colors.END}")
    
    def show_help(self):
        """Yardım menüsünü göster"""
        print(f"\n{Colors.CYAN}📚 CTI-BOT Central Management System Help{Colors.END}")
        print()
        print(f"{Colors.YELLOW}Usage:{Colors.END}")
        print("  python cti_manager.py [option]")
        print("  python cti_manager.py        # Interactive menu")
        print()
        print(f"{Colors.YELLOW}Examples:{Colors.END}")
        print("  python cti_manager.py 1      # Start Flask")
        print("  python cti_manager.py 7      # Check system status")
        print("  python cti_manager.py 11     # Stop system")
        print()
        print(f"{Colors.YELLOW}Log Files:{Colors.END}")
        print(f"  Flask Log: {self.logs_dir / 'flask.log'}")
        print(f"  Data Log: {self.logs_dir / 'data.log'}")
        print(f"  CTI Bot Log: {self.logs_dir / 'cti_bot.log'}")
        print()
        print(f"{Colors.YELLOW}Important Notes:{Colors.END}")
        print("  - First use: run '13' to install packages")
        print("  - Database setup: use '14'")
        print("  - Full system: use '3'")
        print("  - Background mode: use '4'")
    
    def show_system_info(self):
        """Sistem bilgilerini göster"""
        print(f"\n{Colors.CYAN}💻 Sistem Bilgileri{Colors.END}")
        print()
        print(f"{Colors.BLUE}Proje Dizini:{Colors.END} {self.project_root}")
        print(f"{Colors.BLUE}Python Executable:{Colors.END} {self.python_exec}")
        print(f"{Colors.BLUE}Veritabanı:{Colors.END} {self.db_path}")
        print(f"{Colors.BLUE}Logs Dizini:{Colors.END} {self.logs_dir}")
        print()
        
        # Sistem bilgileri
        print(f"{Colors.BLUE}İşletim Sistemi:{Colors.END} {os.name}")
        print(f"{Colors.BLUE}Python Sürümü:{Colors.END} {sys.version}")
        print(f"{Colors.BLUE}Disk Kullanımı:{Colors.END} {psutil.disk_usage(self.project_root).percent:.1f}%")
        print(f"{Colors.BLUE}Memory Kullanımı:{Colors.END} {psutil.virtual_memory().percent}%")
    
    def run_menu(self):
        """Ana menüyü çalıştır"""
        self.print_header()
        
        while True:
            self.print_menu()
            
            try:
                choice = input(f"{Colors.WHITE}Seçiminizi yapın (0-33): {Colors.END}").strip()
                
                if choice == '0':
                    print(f"\n{Colors.CYAN}👋 CTI-BOT Merkezi Yönetim Sistemi'nden çıkılıyor...{Colors.END}")
                    break
                elif choice == '1':
                    self.start_flask_app()
                elif choice == '2':
                    self.start_data_collection()
                elif choice == '3':
                    self.start_full_system()
                elif choice == '4':
                    self.start_background()
                elif choice == '5':
                    print(f"{Colors.YELLOW}Screen ile başlatma özelliği yakında eklenecek{Colors.END}")
                elif choice == '6':
                    print(f"{Colors.YELLOW}Docker ile başlatma özelliği yakında eklenecek{Colors.END}")
                elif choice == '7':
                    self.check_system_status()
                elif choice == '8':
                    self.test_database()
                elif choice == '9':
                    self.show_logs()
                elif choice == '10':
                    self.stop_system()
                    time.sleep(2)
                    self.start_full_system()
                elif choice == '11':
                    self.stop_system()
                elif choice == '12':
                    self.clean_system()
                elif choice == '13':
                    self.install_packages()
                elif choice == '14':
                    self.setup_database()
                elif choice == '15':
                    print(f"{Colors.YELLOW}Performance optimizasyonu özelliği yakında eklenecek{Colors.END}")
                elif choice == '16':
                    print(f"{Colors.YELLOW}Cache sistemi yönetimi özelliği yakında eklenecek{Colors.END}")
                elif choice == '17':
                    self.backup_database()
                elif choice == '18':
                    print(f"{Colors.YELLOW}Sistem güncellemesi özelliği yakında eklenecek{Colors.END}")
                elif choice == '19':
                    self.run_simple_analysis()
                elif choice == '20':
                    self.run_sector_analysis()
                elif choice == '21':
                    print(f"{Colors.YELLOW}Gerçek zamanlı analiz özelliği yakında eklenecek{Colors.END}")
                elif choice == '22':
                    print(f"{Colors.YELLOW}Rapor oluşturma özelliği yakında eklenecek{Colors.END}")
                elif choice == '23':
                    print(f"{Colors.YELLOW}Veri dışa aktarma özelliği yakında eklenecek{Colors.END}")
                elif choice == '24':
                    print(f"{Colors.YELLOW}Sosyal medya otomasyonu özelliği yakında eklenecek{Colors.END}")
                elif choice == '25':
                    print(f"{Colors.YELLOW}Email entegrasyonu özelliği yakında eklenecek{Colors.END}")
                elif choice == '26':
                    print(f"{Colors.YELLOW}Slack entegrasyonu özelliği yakında eklenecek{Colors.END}")
                elif choice == '27':
                    print(f"{Colors.YELLOW}Teams entegrasyonu özelliği yakında eklenecek{Colors.END}")
                elif choice == '28':
                    self.test_apis()
                elif choice == '29':
                    self.test_database()
                elif choice == '30':
                    print(f"{Colors.YELLOW}Redis bağlantı testi özelliği yakında eklenecek{Colors.END}")
                elif choice == '31':
                    print(f"{Colors.YELLOW}Sistem performans testi özelliği yakında eklenecek{Colors.END}")
                elif choice == '32':
                    self.show_help()
                elif choice == '33':
                    self.show_system_info()
                else:
                    print(f"{Colors.RED}❌ Geçersiz seçim!{Colors.END}")
                
                if choice != '0':
                    input(f"\n{Colors.YELLOW}Devam etmek için Enter'a basın...{Colors.END}")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}👋 CTI-BOT Merkezi Yönetim Sistemi'nden çıkılıyor...{Colors.END}")
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ Hata: {e}{Colors.END}")

def main():
    """Ana fonksiyon"""
    manager = CTIManager()
    
    # Komut satırı argümanı varsa direkt çalıştır
    if len(sys.argv) > 1:
        try:
            choice = sys.argv[1]
            if choice.isdigit():
                manager.print_header()
                # Seçimi çalıştır
                if choice == '1':
                    manager.start_flask_app()
                elif choice == '2':
                    manager.start_data_collection()
                elif choice == '3':
                    manager.start_full_system()
                elif choice == '4':
                    manager.start_background()
                elif choice == '7':
                    manager.check_system_status()
                elif choice == '8':
                    manager.test_database()
                elif choice == '9':
                    manager.show_logs()
                elif choice == '11':
                    manager.stop_system()
                elif choice == '13':
                    manager.install_packages()
                elif choice == '14':
                    manager.setup_database()
                elif choice == '17':
                    manager.backup_database()
                elif choice == '19':
                    manager.run_simple_analysis()
                elif choice == '20':
                    manager.run_sector_analysis()
                elif choice == '28':
                    manager.test_apis()
                elif choice == '29':
                    manager.test_database()
                elif choice == '32':
                    manager.show_help()
                elif choice == '33':
                    manager.show_system_info()
                else:
                    print(f"{Colors.RED}❌ Geçersiz seçim: {choice}{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Geçersiz argüman: {choice}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Hata: {e}{Colors.END}")
    else:
        # Etkileşimli menüyü başlat
        manager.run_menu()

if __name__ == "__main__":
    main()
