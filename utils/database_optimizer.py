"""
CTI-BOT Database Optimizer
Database indexing ve query optimizasyonu
"""

from models.DBModel import db, Post, HackedCompany, SocialMediaPost
from sqlalchemy import text, Index
from datetime import datetime, timedelta
import time

class DatabaseOptimizer:
    def __init__(self):
        self.optimization_queries = [
            # Post tablosu için indeksler
            "CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_posts_company_name ON posts(company_name)",
            "CREATE INDEX IF NOT EXISTS idx_posts_sector ON posts(sector)",
            "CREATE INDEX IF NOT EXISTS idx_posts_country ON posts(country)",
            "CREATE INDEX IF NOT EXISTS idx_posts_impact_level ON posts(impact_level)",
            "CREATE INDEX IF NOT EXISTS idx_posts_name ON posts(name)",
            "CREATE INDEX IF NOT EXISTS idx_posts_hack_date ON posts(hack_date)",
            "CREATE INDEX IF NOT EXISTS idx_posts_created_at_sector ON posts(created_at, sector)",
            "CREATE INDEX IF NOT EXISTS idx_posts_created_at_country ON posts(created_at, country)",
            "CREATE INDEX IF NOT EXISTS idx_posts_sector_impact ON posts(sector, impact_level)",
            
            # HackedCompany tablosu için indeksler
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_created_at ON hacked_companies(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_company_name ON hacked_companies(company_name)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_sector ON hacked_companies(sector)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_country_code ON hacked_companies(country_code)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_impact_level ON hacked_companies(impact_level)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_threat_actor ON hacked_companies(threat_actor)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_hack_date ON hacked_companies(hack_date)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_created_at_sector ON hacked_companies(created_at, sector)",
            "CREATE INDEX IF NOT EXISTS idx_hacked_companies_sector_impact ON hacked_companies(sector, impact_level)",
            
            # SocialMediaPost tablosu için indeksler
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_created_at ON social_media_posts(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_platform ON social_media_posts(platform)",
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_content_type ON social_media_posts(content_type)",
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_published_at ON social_media_posts(published_at)",
            "CREATE INDEX IF NOT EXISTS idx_social_media_posts_platform_type ON social_media_posts(platform, content_type)",
        ]
    
    def create_indexes(self):
        """Tüm optimizasyon indekslerini oluştur"""
        print("Database indeksleri oluşturuluyor...")
        start_time = time.time()
        
        try:
            with db.engine.connect() as connection:
                for query in self.optimization_queries:
                    try:
                        connection.execute(text(query))
                        print(f"✓ {query.split('idx_')[1].split(' ON')[0]} indeksi oluşturuldu")
                    except Exception as e:
                        print(f"✗ İndeks oluşturma hatası: {e}")
                
                connection.commit()
            
            end_time = time.time()
            print(f"Database indeksleri başarıyla oluşturuldu ({end_time - start_time:.2f} saniye)")
            return True
            
        except Exception as e:
            print(f"Database indeks oluşturma hatası: {e}")
            return False
    
    def analyze_query_performance(self, query, params=None):
        """Query performansını analiz et"""
        try:
            start_time = time.time()
            
            if params:
                result = db.session.execute(text(query), params)
            else:
                result = db.session.execute(text(query))
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Sonuç sayısını al
            if hasattr(result, 'rowcount'):
                row_count = result.rowcount
            else:
                row_count = len(list(result)) if result else 0
            
            return {
                'execution_time': execution_time,
                'row_count': row_count,
                'query': query,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'query': query,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_table_statistics(self):
        """Tablo istatistiklerini al"""
        try:
            stats = {}
            
            # Post tablosu istatistikleri
            post_count = Post.query.count()
            post_recent = Post.query.filter(Post.created_at >= datetime.utcnow() - timedelta(days=7)).count()
            
            stats['posts'] = {
                'total_count': post_count,
                'recent_7_days': post_recent,
                'avg_per_day': post_recent / 7 if post_recent > 0 else 0
            }
            
            # HackedCompany tablosu istatistikleri
            company_count = HackedCompany.query.count()
            company_recent = HackedCompany.query.filter(HackedCompany.created_at >= datetime.utcnow() - timedelta(days=7)).count()
            
            stats['hacked_companies'] = {
                'total_count': company_count,
                'recent_7_days': company_recent,
                'avg_per_day': company_recent / 7 if company_recent > 0 else 0
            }
            
            # SocialMediaPost tablosu istatistikleri
            social_count = SocialMediaPost.query.count()
            social_recent = SocialMediaPost.query.filter(SocialMediaPost.created_at >= datetime.utcnow() - timedelta(days=7)).count()
            
            stats['social_media_posts'] = {
                'total_count': social_count,
                'recent_7_days': social_recent,
                'avg_per_day': social_recent / 7 if social_recent > 0 else 0
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def optimize_queries(self):
        """Yaygın query'leri optimize et"""
        optimizations = [
            {
                'name': 'Dashboard Overview Query',
                'original': """
                    SELECT COUNT(*) as total_attacks,
                           COUNT(DISTINCT company_name) as unique_companies,
                           COUNT(DISTINCT country) as unique_countries
                    FROM posts 
                    WHERE created_at >= :start_date
                """,
                'optimized': """
                    SELECT COUNT(*) as total_attacks,
                           COUNT(DISTINCT company_name) as unique_companies,
                           COUNT(DISTINCT country) as unique_countries
                    FROM posts 
                    WHERE created_at >= :start_date
                    AND company_name IS NOT NULL
                    AND country IS NOT NULL
                """
            },
            {
                'name': 'Sector Distribution Query',
                'original': """
                    SELECT sector, COUNT(*) as count
                    FROM posts 
                    WHERE created_at >= :start_date
                    GROUP BY sector
                    ORDER BY count DESC
                """,
                'optimized': """
                    SELECT sector, COUNT(*) as count
                    FROM posts 
                    WHERE created_at >= :start_date
                    AND sector IS NOT NULL
                    GROUP BY sector
                    ORDER BY count DESC
                    LIMIT 20
                """
            },
            {
                'name': 'Risk Level Distribution Query',
                'original': """
                    SELECT impact_level, COUNT(*) as count
                    FROM posts 
                    WHERE created_at >= :start_date
                    GROUP BY impact_level
                """,
                'optimized': """
                    SELECT impact_level, COUNT(*) as count
                    FROM posts 
                    WHERE created_at >= :start_date
                    AND impact_level IS NOT NULL
                    GROUP BY impact_level
                    ORDER BY count DESC
                """
            }
        ]
        
        return optimizations
    
    def vacuum_database(self):
        """Database'i temizle ve optimize et (SQLite için)"""
        try:
            print("Database temizleme işlemi başlatılıyor...")
            start_time = time.time()
            
            with db.engine.connect() as connection:
                # SQLite VACUUM komutu
                connection.execute(text("VACUUM"))
                connection.execute(text("ANALYZE"))
                connection.commit()
            
            end_time = time.time()
            print(f"Database temizleme tamamlandı ({end_time - start_time:.2f} saniye)")
            return True
            
        except Exception as e:
            print(f"Database temizleme hatası: {e}")
            return False
    
    def get_index_usage_stats(self):
        """İndeks kullanım istatistiklerini al"""
        try:
            # SQLite için indeks bilgileri
            index_queries = [
                "SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'",
                "PRAGMA index_list(posts)",
                "PRAGMA index_list(hacked_companies)",
                "PRAGMA index_list(social_media_posts)"
            ]
            
            stats = {}
            with db.engine.connect() as connection:
                for i, query in enumerate(index_queries):
                    try:
                        result = connection.execute(text(query))
                        stats[f'query_{i}'] = [dict(row) for row in result]
                    except Exception as e:
                        stats[f'query_{i}'] = {'error': str(e)}
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def run_performance_tests(self):
        """Performans testlerini çalıştır"""
        print("Performans testleri başlatılıyor...")
        
        test_queries = [
            {
                'name': 'Dashboard Overview',
                'query': 'SELECT COUNT(*) FROM posts WHERE created_at >= :start_date',
                'params': {'start_date': datetime.utcnow() - timedelta(days=30)}
            },
            {
                'name': 'Sector Analysis',
                'query': 'SELECT sector, COUNT(*) FROM posts WHERE created_at >= :start_date GROUP BY sector',
                'params': {'start_date': datetime.utcnow() - timedelta(days=30)}
            },
            {
                'name': 'Company Search',
                'query': 'SELECT * FROM posts WHERE company_name LIKE :search LIMIT 100',
                'params': {'search': '%finans%'}
            }
        ]
        
        results = []
        for test in test_queries:
            result = self.analyze_query_performance(test['query'], test['params'])
            result['test_name'] = test['name']
            results.append(result)
        
        return results

# Global database optimizer instance
db_optimizer = DatabaseOptimizer()

