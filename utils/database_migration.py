# Veritabanı Migrasyon Scripti
# Mevcut verileri yeni alanlarla zenginleştirir

import sys
import os
import sqlite3
from datetime import datetime

# Proje root'unu path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sector_detector import SectorDetector

class DatabaseMigration:
    def __init__(self, db_path="instance/data.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.detector = SectorDetector()
        
    def add_new_columns(self):
        """Yeni sütunları ekler"""
        print("Yeni sütunlar ekleniyor...")
        
        # Posts tablosuna yeni sütunlar ekle
        new_columns = [
            "company_name TEXT",
            "sector TEXT",
            "company_size TEXT",
            "impact_level TEXT",
            "employee_count INTEGER",
            "revenue_range TEXT",
            "industry_category TEXT",
            "data_type_leaked TEXT",
            "hack_date DATETIME",
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        ]
        
        for column in new_columns:
            try:
                column_name = column.split()[0]
                self.cur.execute(f"ALTER TABLE posts ADD COLUMN {column}")
                print(f"✓ {column_name} sütunu eklendi")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"⚠ {column_name} sütunu zaten mevcut")
                else:
                    print(f"✗ {column_name} sütunu eklenirken hata: {e}")
        
        # HackedCompany tablosunu oluştur
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS hacked_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                country_code TEXT NOT NULL,
                sector TEXT NOT NULL,
                company_size TEXT NOT NULL,
                hack_date DATETIME NOT NULL,
                threat_actor TEXT NOT NULL,
                data_type_leaked TEXT,
                impact_level TEXT NOT NULL,
                company_website TEXT,
                revenue_range TEXT,
                employee_count INTEGER,
                industry_category TEXT,
                post_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """)
        print("✓ HackedCompany tablosu oluşturuldu")
        
        # SocialMediaPost tablosunu oluştur
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS social_media_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                image_url TEXT,
                hashtags TEXT,
                engagement_metrics TEXT,
                published_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ SocialMediaPost tablosu oluşturuldu")
        
        self.conn.commit()
    
    def enrich_existing_posts(self):
        """Mevcut postları zenginleştirir"""
        print("Mevcut postlar zenginleştiriliyor...")
        
        # Tüm postları al
        self.cur.execute("SELECT id, title, website, description, country, name FROM posts")
        posts = self.cur.fetchall()
        
        print(f"Toplam {len(posts)} post bulundu")
        
        for i, post in enumerate(posts):
            post_id, title, website, description, country, threat_actor = post
            
            print(f"İşleniyor: {i+1}/{len(posts)} - {title[:50]}...")
            
            # Sektör tespiti
            post_data = {
                'title': title or '',
                'website': website or '',
                'description': description or '',
                'country': country or ''
            }
            
            analysis = self.detector.analyze_post(post_data)
            
            # Hack tarihini parse et
            hack_date = datetime.now()
            try:
                # Eğer published alanı varsa onu kullan
                self.cur.execute("SELECT published FROM posts WHERE id = ?", (post_id,))
                published = self.cur.fetchone()[0]
                if published and published != "None":
                    hack_date = datetime.strptime(published, "%Y-%m-%d")
            except:
                pass
            
            # Post'u güncelle
            self.cur.execute("""
                UPDATE posts SET 
                    company_name = ?,
                    sector = ?,
                    company_size = ?,
                    impact_level = ?,
                    employee_count = ?,
                    revenue_range = ?,
                    industry_category = ?,
                    data_type_leaked = ?,
                    hack_date = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
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
                post_id
            ))
            
            # HackedCompany tablosuna da ekle
            self.cur.execute("""
                INSERT OR REPLACE INTO hacked_companies 
                (company_name, country_code, sector, company_size, hack_date, threat_actor,
                 data_type_leaked, impact_level, company_website, revenue_range, employee_count,
                 industry_category, post_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis['company_name'],
                country or 'Bilinmeyen',
                analysis['sector'],
                analysis['company_size'],
                hack_date,
                threat_actor or 'Bilinmeyen',
                analysis['data_type_leaked'],
                analysis['impact_level'],
                website or '',
                analysis['revenue_range'],
                analysis['employee_count'],
                analysis['industry_category'],
                post_id,
                datetime.now(),
                datetime.now()
            ))
        
        self.conn.commit()
        print("✓ Tüm postlar zenginleştirildi")
    
    def create_indexes(self):
        """Performans için indexler oluşturur"""
        print("Indexler oluşturuluyor...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_posts_sector ON posts(sector)",
            "CREATE INDEX IF NOT EXISTS idx_posts_country ON posts(country)",
            "CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_posts_impact_level ON posts(impact_level)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_sector ON hacked_companies(sector)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_country_code ON hacked_companies(country_code)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_hack_date ON hacked_companies(hack_date)",
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_platform ON social_media_posts(platform)",
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_published_at ON social_media_posts(published_at)"
        ]
        
        for index_sql in indexes:
            try:
                self.cur.execute(index_sql)
                print(f"✓ Index oluşturuldu: {index_sql.split()[-1]}")
            except Exception as e:
                print(f"✗ Index oluşturulurken hata: {e}")
        
        self.conn.commit()
    
    def run_migration(self):
        """Tam migrasyonu çalıştırır"""
        print("=" * 50)
        print("VERİTABANI MİGRASYONU BAŞLATIYOR")
        print("=" * 50)
        
        try:
            # 1. Yeni sütunları ekle
            self.add_new_columns()
            
            # 2. Mevcut postları zenginleştir
            self.enrich_existing_posts()
            
            # 3. Indexleri oluştur
            self.create_indexes()
            
            print("=" * 50)
            print("MİGRASYON TAMAMLANDI!")
            print("=" * 50)
            
            # İstatistikleri göster
            self.show_statistics()
            
        except Exception as e:
            print(f"✗ Migrasyon sırasında hata: {e}")
            self.conn.rollback()
        finally:
            self.conn.close()
    
    def show_statistics(self):
        """Migrasyon sonrası istatistikleri gösterir"""
        print("\n📊 MİGRASYON İSTATİSTİKLERİ:")
        
        # Posts tablosu istatistikleri
        self.cur.execute("SELECT COUNT(*) FROM posts")
        total_posts = self.cur.fetchone()[0]
        
        self.cur.execute("SELECT COUNT(*) FROM posts WHERE sector IS NOT NULL")
        enriched_posts = self.cur.fetchone()[0]
        
        print(f"📝 Toplam post sayısı: {total_posts}")
        print(f"✅ Zenginleştirilmiş post sayısı: {enriched_posts}")
        
        # Sektör dağılımı
        self.cur.execute("SELECT sector, COUNT(*) FROM posts WHERE sector IS NOT NULL GROUP BY sector ORDER BY COUNT(*) DESC LIMIT 5")
        sector_stats = self.cur.fetchall()
        
        print(f"\n🏢 En çok saldırı alan sektörler:")
        for sector, count in sector_stats:
            print(f"   {sector}: {count}")
        
        # Ülke dağılımı
        self.cur.execute("SELECT country, COUNT(*) FROM posts WHERE country IS NOT NULL GROUP BY country ORDER BY COUNT(*) DESC LIMIT 5")
        country_stats = self.cur.fetchall()
        
        print(f"\n🌍 En çok saldırı alan ülkeler:")
        for country, count in country_stats:
            print(f"   {country}: {count}")
        
        # Etki seviyesi dağılımı
        self.cur.execute("SELECT impact_level, COUNT(*) FROM posts WHERE impact_level IS NOT NULL GROUP BY impact_level")
        impact_stats = self.cur.fetchall()
        
        print(f"\n⚠️ Etki seviyesi dağılımı:")
        for impact, count in impact_stats:
            print(f"   {impact}: {count}")

if __name__ == "__main__":
    migration = DatabaseMigration()
    migration.run_migration()

