"""
CTI-BOT Performance Migration
Database optimizasyonu ve cache kurulumu için migration scripti
"""

from flask import Flask
from models.DBModel import db
from utils.database_optimizer import db_optimizer
from utils.cache_manager import cache_manager
import os

def run_performance_migration():
    """Performance optimizasyonu migration'ını çalıştır"""
    print("🚀 CTI-BOT Performance Migration başlatılıyor...")
    
    # Flask uygulamasını başlat
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    
    with app.app_context():
        try:
            print("\n📊 1. Database İndeksleri Oluşturuluyor...")
            index_result = db_optimizer.create_indexes()
            if index_result:
                print("✅ Database indeksleri başarıyla oluşturuldu")
            else:
                print("❌ Database indeksleri oluşturulurken hata oluştu")
            
            print("\n🧹 2. Database Temizleme İşlemi...")
            vacuum_result = db_optimizer.vacuum_database()
            if vacuum_result:
                print("✅ Database temizleme işlemi tamamlandı")
            else:
                print("❌ Database temizleme işlemi başarısız")
            
            print("\n📈 3. Performans Testleri Çalıştırılıyor...")
            performance_tests = db_optimizer.run_performance_tests()
            print(f"✅ {len(performance_tests)} performans testi tamamlandı")
            
            print("\n💾 4. Cache Sistemi Kontrol Ediliyor...")
            cache_stats = cache_manager.get_cache_stats()
            if cache_stats['status'] == 'enabled':
                print("✅ Cache sistemi aktif")
                print(f"   - Bağlı istemci sayısı: {cache_stats.get('connected_clients', 0)}")
                print(f"   - Kullanılan bellek: {cache_stats.get('used_memory', 'N/A')}")
            else:
                print("⚠️ Cache sistemi devre dışı")
                print(f"   - Durum: {cache_stats.get('status', 'unknown')}")
                print(f"   - Mesaj: {cache_stats.get('message', 'N/A')}")
            
            print("\n📊 5. Database İstatistikleri...")
            db_stats = db_optimizer.get_table_statistics()
            for table, stats in db_stats.items():
                if isinstance(stats, dict) and 'total_count' in stats:
                    print(f"   - {table}: {stats['total_count']} kayıt")
                    print(f"     Son 7 gün: {stats.get('recent_7_days', 0)} kayıt")
                    print(f"     Günlük ortalama: {stats.get('avg_per_day', 0):.1f} kayıt")
            
            print("\n🎉 Performance Migration tamamlandı!")
            print("\n📋 Özet:")
            print(f"   - Database indeksleri: {'✅' if index_result else '❌'}")
            print(f"   - Database temizleme: {'✅' if vacuum_result else '❌'}")
            print(f"   - Cache sistemi: {'✅' if cache_stats['status'] == 'enabled' else '⚠️'}")
            print(f"   - Performans testleri: ✅ {len(performance_tests)} test")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration hatası: {e}")
            return False

def check_redis_connection():
    """Redis bağlantısını kontrol et"""
    print("\n🔍 Redis Bağlantı Kontrolü...")
    
    try:
        import redis
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        r.ping()
        print(f"✅ Redis bağlantısı başarılı ({redis_host}:{redis_port})")
        return True
    except Exception as e:
        print(f"❌ Redis bağlantı hatası: {e}")
        print("💡 Redis kurulumu için:")
        print("   - Windows: https://github.com/microsoftarchive/redis/releases")
        print("   - Linux: sudo apt-get install redis-server")
        print("   - Docker: docker run -d -p 6379:6379 redis:alpine")
        return False

def install_requirements():
    """Gerekli paketleri yükle"""
    print("\n📦 Gerekli Paketler Yükleniyor...")
    
    try:
        import subprocess
        import sys
        
        packages = [
            'redis',
            'pandas',
            'openpyxl',
            'reportlab',
            'flask-cors',
            'flask-limiter'
        ]
        
        for package in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} yüklendi")
            except subprocess.CalledProcessError:
                print(f"❌ {package} yüklenemedi")
        
        return True
    except Exception as e:
        print(f"❌ Paket yükleme hatası: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CTI-BOT Performance Migration")
    print("=" * 60)
    
    # 1. Gerekli paketleri kontrol et
    print("\n1️⃣ Gerekli Paketler Kontrol Ediliyor...")
    install_requirements()
    
    # 2. Redis bağlantısını kontrol et
    print("\n2️⃣ Redis Bağlantısı Kontrol Ediliyor...")
    redis_ok = check_redis_connection()
    
    # 3. Performance migration'ını çalıştır
    print("\n3️⃣ Performance Migration Çalıştırılıyor...")
    migration_ok = run_performance_migration()
    
    # 4. Sonuç
    print("\n" + "=" * 60)
    if migration_ok:
        print("🎉 Performance Migration başarıyla tamamlandı!")
        print("\n📋 Yeni API Endpoint'leri:")
        print("   - GET /api/cache/stats - Cache istatistikleri")
        print("   - POST /api/cache/clear - Cache temizleme")
        print("   - GET /api/database/stats - Database istatistikleri")
        print("   - POST /api/database/optimize - Database optimizasyonu")
        print("   - GET /api/performance/monitor - Performans izleme")
        print("   - POST /api/performance/auto-optimize - Otomatik optimizasyon")
    else:
        print("❌ Performance Migration başarısız!")
        print("Lütfen hataları kontrol edin ve tekrar deneyin.")
    
    print("=" * 60)

