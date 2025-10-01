import requests
import sqlite3
import json
import hashlib
import re
import os
import time
import sys
from playwright.sync_api import sync_playwright
from datetime import datetime

# Utils modüllerini import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Veritabanı bağlantısı ve tablo oluşturma
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

# instance dizinini oluştur
instance_dir = current_directory + "instance"
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)
    print(f"✅ instance dizini oluşturuldu: {instance_dir}")

# Veritabanı bağlantısı
db_path = current_directory + "instance/data.db"
print(f"📊 Veritabanı yolu: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print("✅ Veritabanı bağlantısı başarılı")
    
    # Tabloları oluştur
    print("📊 Tablolar oluşturuluyor...")
    
    # Posts tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        company_name TEXT,
        country TEXT,
        sector TEXT,
        impact_level TEXT,
        website TEXT,
        description TEXT,
        hack_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Groups tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        description TEXT,
        website TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Wallets tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT UNIQUE,
        balance REAL,
        balance_usd REAL,
        blockchain TEXT,
        family TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Transactions tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER,
        hash TEXT UNIQUE,
        time TIMESTAMP,
        amount REAL,
        amount_usd REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wallet_id) REFERENCES wallets (id)
    )
    ''')
    
    conn.commit()
    print("✅ Tablolar oluşturuldu")
    
except Exception as e:
    print(f"❌ Veritabanı bağlantı hatası: {e}")
    exit(1)

# Sektör tespit algoritması (opsiyonel)
try:
    from utils.sector_detector import SectorDetector
    sector_detector = SectorDetector()
except ImportError:
    print("SectorDetector modülü bulunamadı, basit sektör tespiti kullanılacak")
    sector_detector = None

# 2. POST verilerini çekme ve veritabanına ekleme
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1360155723081715792/hhJkkp6yFF5iCLp_ggSzmD6EHXiKi6uSTP5Pf0TcyFNeXPhHCzBz1Qz_MFqB5XZ0qGPH"
RANSOMWARE_GROUPS = "https://api.ransomware.live/v2/groups"
RANSOMWARE_POSTS = "https://data.ransomware.live/posts.json"
RANSOMWARE_CRYPTO = "https://api.ransomwhe.re/export"
DATE_DATA = str(datetime.now()).replace(".","_").replace(":","_").replace(" ","_")

# Örnek veri ekleme fonksiyonu
def add_sample_data():
    """Örnek veri ekle"""
    print("📊 Örnek veri ekleniyor...")
    
    sample_posts = [
        {
            'title': 'LockBit Ransomware Attack',
            'name': 'LockBit',
            'description': 'Ransomware saldırısı - Örnek Şirket A',
            'discovered': '2024-09-28',
            'published': '2024-09-28',
            'post_url': 'https://example.com',
            'country': 'TR',
            'activity': 'High',
            'website': 'https://example.com',
            'duplicates': 0,
            'screenshot': 'screenshot1.png'
        },
        {
            'title': 'Conti Data Breach',
            'name': 'Conti',
            'description': 'Veri sızıntısı - Örnek Şirket B',
            'discovered': '2024-09-27',
            'published': '2024-09-27',
            'post_url': 'https://example2.com',
            'country': 'US',
            'activity': 'Critical',
            'website': 'https://example2.com',
            'duplicates': 0,
            'screenshot': 'screenshot2.png'
        },
        {
            'title': 'REvil System Compromise',
            'name': 'REvil',
            'description': 'Sistem ele geçirme - Örnek Şirket C',
            'discovered': '2024-09-26',
            'published': '2024-09-26',
            'post_url': 'https://example3.com',
            'country': 'UK',
            'activity': 'Medium',
            'website': 'https://example3.com',
            'duplicates': 0,
            'screenshot': 'screenshot3.png'
        }
    ]
    
    # Önce mevcut tablo yapısını kontrol et
    cur.execute("PRAGMA table_info(posts)")
    columns = [col[1] for col in cur.fetchall()]
    print(f"📊 Mevcut posts tablosu sütunları: {columns}")
    
    # Mevcut sütunlara göre veri ekle
    for post in sample_posts:
        # Mevcut tablo yapısına uygun veri ekleme
        cur.execute('''
            INSERT OR IGNORE INTO posts (name, company_name, country, sector, impact_level, website, description, hack_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post['name'],
            post['name'],  # company_name olarak name kullan
            post['country'],
            'Technology',  # sector
            post['activity'],  # impact_level olarak activity kullan
            post['website'],
            post['description'],
            post['discovered']  # hack_date olarak discovered kullan
        ))
    
    conn.commit()
    print("✅ Örnek veri eklendi")

def data_download_archive(DOWNLOAD_URL, FILE_NAME):
    if not os.path.exists(current_directory + "data_archive"):
        os.makedirs(current_directory + "data_archive")
    try:
        response = requests.get(DOWNLOAD_URL, stream=True)
        response.raise_for_status()
        with open(current_directory + "data_archive/" + FILE_NAME, 'wb') as dosya:
            for parca in response.iter_content(chunk_size=8192):
                if parca:
                    dosya.write(parca)
    except requests.exceptions.RequestException:
        return "False"

def generate_md5_from_string(text):
    md5_hash = hashlib.md5()
    md5_hash.update(text.encode('utf-8'))  # Veriyi encode edip hash'e ekliyoruz
    return str(md5_hash.hexdigest())  # Hash'i hexadecimal (hex) formatında döndürür

def send_discord_message(content):
    data = {"content": content}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers=headers)
        if response.status_code == 204:
            print("Discord mesajı gönderildi.")
        else:
            print("Discord mesajı gönderilemedi:", response.status_code)
    except Exception as e:
        print("Discord mesaj hatası:", e)

# playwright install-deps and playwright install komutunu girmeyi unutma!
def capture_screenshot(url, output_filename):
    if url and url != "None" and len(url.strip()) > 0:
        try:
            with sync_playwright() as p:
                print(str(url) + " sitesine bağlanıyor...")
                browser = p.chromium.launch(proxy={"server": "socks5://127.0.0.1:9055"}, args=[''])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    viewport={"width": 1280, "height": 800},
                    locale='en-US',
                    ignore_https_errors=True)
                page = context.new_page()
                page.goto(url, wait_until='domcontentloaded', timeout=15000)
                page.bring_to_front()
                page.wait_for_timeout(15000)
                page.mouse.move(x=500, y=400)
                page.wait_for_load_state('networkidle')
                page.mouse.wheel(delta_y=2000, delta_x=0)
                page.wait_for_load_state('networkidle')
                if not os.path.exists(current_directory + "screenshots"):
                    os.makedirs(current_directory + "screenshots")
                page.screenshot(path=current_directory + "screenshots/" + output_filename + ".png", full_page=True)
                return output_filename
        except:
            return "ConnectionError"
    else:
        return "None"
    
# 1. GRUP verilerini çekme ve veritabanına ekleme
def fetch_and_store_groups():
    print("Gruplar alınıyor...")
    response = requests.get(RANSOMWARE_GROUPS)
    data_download_archive(RANSOMWARE_GROUPS, "groups-" + DATE_DATA + ".json")
    if response.status_code == 200:
        groups = response.json()
        for group in groups:
            name = group.get("name", "None")
            url = group.get("url", "None")

            # Aynı name ve url varsa kaydı atla
            cur.execute("""
                SELECT * FROM groups WHERE name = ? AND url = ?
            """, (name, url))

            if cur.fetchone():
                print(f"Zaten mevcut: {name}, atlanıyor.")
            else:
                discord_msg = f"SyberCTI Bot\n🇹🇷 Yeni bir tehdit aktörü keşfedildi.\nAdı : {name}\nWebsitesi : {url}"
                send_discord_message(discord_msg)
                cur.execute("""
                            INSERT OR REPLACE INTO groups (locations, meta, name, profile, tools, ttps, url)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (
                                json.dumps(group.get("locations")),
                                group.get("meta", "None"),
                                name,
                                json.dumps(group.get("profile")),
                                json.dumps(group.get("tools")),
                                json.dumps(group.get("ttps")),
                                url
                                ))
                print(str(group.get("name", "None")) + " başarıyla kaydedildi")
                conn.commit()
                print(f"{name} başarıyla kaydedildi")
            print(f"{len(groups)} grup işlendi.")
    else:
        print("Gruplar alınamadı:", response.status_code)

# Ransomware olaylarını koy
def fetch_and_store_posts():
    print("Postlar alınıyor...")
    response = requests.get(RANSOMWARE_POSTS)
    data_download_archive(RANSOMWARE_POSTS, "posts-" + DATE_DATA + ".json")
    if response.status_code == 200:
        posts = response.json()
        for post in posts:
            # Gerekli alanları al
            group_name = post.get("group_name", "None")
            post_url = post.get('post_url', 'None')
            post_title = post.get("post_title", "None")
            discovered = post.get("discovered", "None")
            published = post.get("published", "None")
            website = post.get("website", "None")
            country = post.get("country", "None")
            if post_url == "" or post_url is None:
                post_url = "Herhangi bir onion link bulunamadı ve/veya onion link üzerinde paylaşılmadı"
            # Veritabanında bu kayıt zaten var mı?
            cur.execute("""
                SELECT * FROM posts
                WHERE title = ? AND discovered = ? AND published = ? AND website = ? AND country = ?
            """, (post_title, discovered, published, website, country))

            if cur.fetchone():
                print(f"Zaten mevcut: {post_title}, atlanıyor.")
                continue  # Bu kayıt zaten varsa, atla
            else:
                get_screenshot = capture_screenshot(
                    str(post.get("post_url", "None")),
                    generate_md5_from_string(post_title)
                    )
                # Yeni kayıt ekle
                if country == "TR":
                    discord_msg = f"SyberCTI Bot\n🇹🇷 Yeni yetkisiz erişim saldırısına uğrayan alan: {post_title}\nTehdit Aktörü Adı :\n{group_name}🔗\nTarih : {published}\nSızıntı URL : {post_url}"
                    send_discord_message(discord_msg)
                elif country == "None" or country == "":
                    if website != "None" or website != "":
                        pattern = r'https?://(?:[\w.-]+\.)?[\w-]+\.(?:com|ct)\.tr(?:/[^\s]*)?|(?:[\w-]+\.)?[\w-]+\.(?:com|ct)\.tr'
                        matches = re.findall(pattern, website)
                        for match in matches:
                            discord_msg = f"SyberCTI Bot\n🇹🇷 Yeni yetkisiz erişim saldırısına uğrayan alan: {match}\nTehdit Aktörü Adı :\n{group_name}🔗\nWebsitesi : {website}\nTarih : {published}\nSızıntı URL : {post_url}"
                            send_discord_message(discord_msg)
                # Sektör tespiti ve veri zenginleştirme
                post_data = {
                    'title': post_title,
                    'website': website,
                    'description': post.get("description", "None"),
                    'country': country
                }
                
                if sector_detector:
                    analysis = sector_detector.analyze_post(post_data)
                else:
                    # Basit sektör tespiti
                    analysis = {
                        'sector': 'Unknown',
                        'company_size': 'Unknown',
                        'impact_level': 'Medium'
                    }
                
                # Hack tarihini parse et
                hack_date = None
                try:
                    if published and published != "None":
                        hack_date = datetime.strptime(published, "%Y-%m-%d")
                except:
                    hack_date = datetime.now()
                
                cur.execute("""
                            INSERT OR REPLACE INTO posts (title, name, description, discovered, published, post_url, country, activity, website, duplicates, screenshot,
                                                         company_name, sector, company_size, impact_level, employee_count, revenue_range, industry_category, 
                                                         data_type_leaked, hack_date, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                post_title,
                                post.get("group_name", "None"),
                                post.get("description", "None"),
                                discovered,
                                published,
                                post.get("post_url", "None"),
                                country,
                                post.get("activity", "None"),
                                website,
                                json.dumps(post.get("duplicates")),
                                get_screenshot,
                                analysis['company_name'],
                                analysis['sector'],
                                analysis['company_size'],
                                analysis['impact_level'],
                                analysis['employee_count'],
                                analysis['revenue_range'],
                                analysis['industry_category'],
                                analysis['data_type_leaked'],
                                hack_date,
                                datetime.now(),
                                datetime.now()
                                ))
                conn.commit()
                print(f"{post_title} başarıyla kaydedildi")
        print(f"{len(posts)} post işlendi.")
    else:
        return "None"


def fetch_and_store_wallets_from_api():
    print("Veriler API üzerinden alınıyor...")

    response = requests.get(RANSOMWARE_CRYPTO)
    data_download_archive(RANSOMWARE_CRYPTO, "wallets-" + DATE_DATA + ".json")
    if response.status_code != 200:
        send_discord_message("SyberCTI - Ransomware Kripto Cüzdan değişiklikleri alınamadı!\nVeri kaynağına bağlantı sağlanamadı.")
        print("Veri alınamadı. Durum kodu:", response.status_code)
        return

    try:
        wallet_list = response.json()
    except Exception as e:
        print("JSON ayrıştırma hatası veya veri formatı hatası:", e)
        return

    for wallet in wallet_list["result"]:
        address = str(wallet["address"])
        balance = int(wallet["balance"])
        balance_usd = float(wallet["balanceUSD"])
        blockchain = str(wallet["blockchain"])
        created_at = str(wallet["createdAt"])
        updated_at = str(wallet["updatedAt"])
        family = str(wallet["family"])
        if balance is None:
            balance = 0
        if balance_usd is None:
            balance_usd = 0.0
        if blockchain is None:
            blockchain = "none"
    
        cur.execute("SELECT * FROM wallets WHERE address = ?", (address,))
        if cur.fetchone():
            print(f"Zaten mevcut: {address}, değişikliğe bakılıyor.")
            # Bakiye farklı mı kontrol et
            cur.execute("SELECT balance FROM wallets WHERE address = ?", (address,))
            row = cur.fetchone()
            if row:
                old_balance = row[0]
                if old_balance != balance:
                    cur.execute('''
                    INSERT INTO kripto_degisim (tarih, cuzdanno, degismeden_once, degisimden_sonra)
                    VALUES (?, ?, ?)
                    ''', (datetime.utcnow().isoformat(), address, old_balance))
                    print(f"Zaten mevcut: {address}, değişiklik tespit edildi.")
                    send_discord_message("SyberCTI - Ransomware Kripto Cüzdan İstihbarat Modülü\nKripto varlıkta hareket keşfedildi!\nAdresi: {address}\nKripto Varlık Tipi:{blockchain}\nTehdit Aktörü:{family}\nOluşturulma Tarihi:{created_at}\nDeğişim Miktarı {old_balance} → {balance}")
            else:
                print(f"Zaten mevcut: {address}, değişiklik yok.")
        else:
            cur.execute('''
                        INSERT INTO wallets (address, balance, balance_usd, blockchain, created_at, updated_at, family)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (address, balance, balance_usd, blockchain, created_at, updated_at, family))
            print(f"{address} cüzdanı kaydedildi.")
            for tx in wallet.get("transactions", []):
                tx_hash = tx.get("hash")
                tx_time = tx.get("time")
                tx_amount = tx.get("amount")
                tx_amount_usd = tx.get("amountUSD", 0.0)
                cur.execute("SELECT * FROM transactions WHERE hash = ?", (tx_hash,))
                if cur.fetchone():
                    continue

                # wallet_id'yi bul
                cur.execute("SELECT id FROM wallets WHERE address = ?", (address,))
                row = cur.fetchone()
                if row:
                    wallet_id = row[0]
                else:
                    print(f"Wallet ID alınamadı: {address}")
                    continue

                cur.execute('''
                            INSERT INTO transactions (wallet_id, hash, time, amount, amount_usd)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (wallet_id, tx_hash, tx_time, tx_amount, tx_amount_usd))
                send_discord_message("SyberCTI - Ransomware Kripto Cüzdan İstihbarat Modülü\nYeni kripto varlık keşfedildi!\nAdresi: {address}\nKripto Varlık Tipi:{blockchain}\nTehdit Aktörü:{family}\nOluşturulma Tarihi:{created_at}\nİçerisinde Bulunan Miktar (USD):{balance_usd}")
                conn.commit()
    print(f"{len(address)} cüzdan işlendi.")

if __name__ == "__main__":
    print("🚀 CTI-BOT Veri Toplama Başlatılıyor...")
    print("=" * 50)
    
    # Önce örnek veri ekle
    add_sample_data()
    
    # Sadece örnek veri ekleme modu (test için)
    print("✅ Örnek veri eklendi, veri toplama tamamlandı!")
    print("💡 Gerçek veri toplama için ayrı terminal açın ve şu komutu çalıştırın:")
    print("   python3 background_jobs/cron_update_db.py")
    
    conn.close()
    print("✅ Veritabanı bağlantısı kapatıldı")