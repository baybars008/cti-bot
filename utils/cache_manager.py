"""
CTI-BOT Cache Manager
Redis tabanlı caching sistemi
"""

import redis
import json
import pickle
import os
from datetime import datetime, timedelta
from flask import current_app

class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.enabled = True
        self.default_ttl = 3600  # 1 saat
        self._init_redis()
    
    def _init_redis(self):
        """Redis bağlantısını başlat"""
        try:
            # Redis konfigürasyonu
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_db = int(os.getenv('REDIS_DB', 0))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=False,  # Binary data için
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Bağlantıyı test et
            self.redis_client.ping()
            print("Redis cache sistemi başarıyla başlatıldı")
            
        except Exception as e:
            print(f"Redis bağlantı hatası: {e}")
            print("Cache sistemi devre dışı bırakıldı")
            self.enabled = False
            self.redis_client = None
    
    def get(self, key):
        """Cache'den veri al"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Cache get hatası: {e}")
            return None
    
    def set(self, key, value, ttl=None):
        """Cache'e veri kaydet"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            serialized_data = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized_data)
        except Exception as e:
            print(f"Cache set hatası: {e}")
            return False
    
    def delete(self, key):
        """Cache'den veri sil"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete hatası: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Belirli pattern'e uyan tüm cache'leri sil"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear pattern hatası: {e}")
            return False
    
    def get_or_set(self, key, func, ttl=None, *args, **kwargs):
        """Cache'den al, yoksa fonksiyonu çalıştır ve cache'e kaydet"""
        # Önce cache'den kontrol et
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        # Cache'de yoksa fonksiyonu çalıştır
        try:
            data = func(*args, **kwargs)
            if data is not None:
                self.set(key, data, ttl)
            return data
        except Exception as e:
            print(f"Cache get_or_set fonksiyon hatası: {e}")
            return None
    
    def invalidate_dashboard_cache(self):
        """Dashboard cache'ini temizle"""
        patterns = [
            'dashboard:*',
            'statistics:*',
            'charts:*',
            'analytics:*'
        ]
        
        for pattern in patterns:
            self.clear_pattern(pattern)
        print("Dashboard cache temizlendi")
    
    def invalidate_export_cache(self):
        """Export cache'ini temizle"""
        patterns = [
            'export:*',
            'reports:*'
        ]
        
        for pattern in patterns:
            self.clear_pattern(pattern)
        print("Export cache temizlendi")
    
    def get_cache_stats(self):
        """Cache istatistiklerini al"""
        if not self.enabled or not self.redis_client:
            return {
                'status': 'disabled',
                'message': 'Cache sistemi devre dışı'
            }
        
        try:
            info = self.redis_client.info()
            return {
                'status': 'enabled',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# Global cache manager instance
cache_manager = CacheManager()

# Cache decorator
def cache_result(ttl=3600, key_prefix=''):
    """Fonksiyon sonucunu cache'leyen decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Cache key oluştur
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Cache'den al
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Fonksiyonu çalıştır ve cache'e kaydet
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Özel cache key'leri
class CacheKeys:
    DASHBOARD_OVERVIEW = "dashboard:overview"
    DASHBOARD_STATISTICS = "dashboard:statistics"
    CHARTS_HEATMAP = "charts:heatmap"
    CHARTS_RISK_TREND = "charts:risk_trend"
    CHARTS_SECTOR_RADAR = "charts:sector_radar"
    ANALYTICS_TRENDS = "analytics:trends"
    EXPORT_ATTACKS = "export:attacks"
    EXPORT_COMPANIES = "export:companies"
    API_HEALTH = "api:health"
    
    @staticmethod
    def get_dashboard_key(days=30):
        return f"dashboard:overview:{days}"
    
    @staticmethod
    def get_charts_key(chart_type, days=30):
        return f"charts:{chart_type}:{days}"
    
    @staticmethod
    def get_export_key(export_type, format_type, days=30):
        return f"export:{export_type}:{format_type}:{days}"
