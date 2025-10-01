"""
CTI-BOT Monitoring System
Error tracking, performance monitoring ve alerting sistemi
"""

import logging
import time
import psutil
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app
import json

class MonitoringSystem:
    def __init__(self):
        self.setup_logging()
        self.performance_metrics = {
            'response_times': [],
            'error_counts': {},
            'memory_usage': [],
            'cpu_usage': [],
            'database_queries': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.alert_thresholds = {
            'response_time_ms': 5000,  # 5 saniye
            'memory_usage_percent': 80,  # %80
            'cpu_usage_percent': 90,  # %90
            'error_rate_percent': 5,  # %5
            'database_query_time_ms': 2000  # 2 saniye
        }
    
    def setup_logging(self):
        """Logging sistemini kur"""
        # Log dosyası oluştur
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Logger konfigürasyonu
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/cti_bot.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('CTI-BOT')
    
    def track_performance(self, func_name):
        """Fonksiyon performansını izle"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    success = False
                    error = str(e)
                    self.logger.error(f"Error in {func_name}: {e}")
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    
                    response_time = (end_time - start_time) * 1000  # ms
                    memory_delta = end_memory - start_memory
                    
                    # Metrikleri kaydet
                    self.performance_metrics['response_times'].append({
                        'function': func_name,
                        'response_time_ms': response_time,
                        'timestamp': datetime.now().isoformat(),
                        'success': success,
                        'memory_delta_mb': memory_delta
                    })
                    
                    # Son 100 kaydı tut
                    if len(self.performance_metrics['response_times']) > 100:
                        self.performance_metrics['response_times'] = self.performance_metrics['response_times'][-100:]
                    
                    # Hata sayısını güncelle
                    if not success:
                        if func_name not in self.performance_metrics['error_counts']:
                            self.performance_metrics['error_counts'][func_name] = 0
                        self.performance_metrics['error_counts'][func_name] += 1
                    
                    # Sistem kaynaklarını izle
                    self._track_system_resources()
                    
                    # Alert kontrolü
                    self._check_alerts(func_name, response_time, success)
                
                return result
            return wrapper
        return decorator
    
    def _track_system_resources(self):
        """Sistem kaynaklarını izle"""
        try:
            # Memory kullanımı
            memory_percent = psutil.virtual_memory().percent
            self.performance_metrics['memory_usage'].append({
                'percent': memory_percent,
                'timestamp': datetime.now().isoformat()
            })
            
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            self.performance_metrics['cpu_usage'].append({
                'percent': cpu_percent,
                'timestamp': datetime.now().isoformat()
            })
            
            # Son 100 kaydı tut
            for metric in ['memory_usage', 'cpu_usage']:
                if len(self.performance_metrics[metric]) > 100:
                    self.performance_metrics[metric] = self.performance_metrics[metric][-100:]
                    
        except Exception as e:
            self.logger.error(f"System resource tracking error: {e}")
    
    def _check_alerts(self, func_name, response_time, success):
        """Alert kontrolü yap"""
        try:
            # Response time alert
            if response_time > self.alert_thresholds['response_time_ms']:
                self._send_alert('PERFORMANCE', f"Slow response in {func_name}: {response_time:.2f}ms")
            
            # Error rate alert
            if not success:
                total_requests = len(self.performance_metrics['response_times'])
                error_count = sum(1 for r in self.performance_metrics['response_times'] if not r['success'])
                error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
                
                if error_rate > self.alert_thresholds['error_rate_percent']:
                    self._send_alert('ERROR_RATE', f"High error rate: {error_rate:.2f}%")
            
            # Memory usage alert
            if self.performance_metrics['memory_usage']:
                latest_memory = self.performance_metrics['memory_usage'][-1]['percent']
                if latest_memory > self.alert_thresholds['memory_usage_percent']:
                    self._send_alert('MEMORY', f"High memory usage: {latest_memory:.2f}%")
            
            # CPU usage alert
            if self.performance_metrics['cpu_usage']:
                latest_cpu = self.performance_metrics['cpu_usage'][-1]['percent']
                if latest_cpu > self.alert_thresholds['cpu_usage_percent']:
                    self._send_alert('CPU', f"High CPU usage: {latest_cpu:.2f}%")
                    
        except Exception as e:
            self.logger.error(f"Alert check error: {e}")
    
    def _send_alert(self, alert_type, message):
        """Alert gönder"""
        try:
            alert_data = {
                'type': alert_type,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'severity': 'WARNING'
            }
            
            # Log'a kaydet
            self.logger.warning(f"ALERT: {alert_type} - {message}")
            
            # Integration manager'a gönder
            from utils.integration_manager import integration_manager
            integration_manager.send_system_alert(
                alert_type, 
                message, 
                severity='warning',
                platforms=['slack', 'teams']
            )
            
        except Exception as e:
            self.logger.error(f"Alert sending error: {e}")
    
    def track_database_query(self, query, execution_time, success=True):
        """Database query performansını izle"""
        try:
            self.performance_metrics['database_queries'].append({
                'query': query[:100] + '...' if len(query) > 100 else query,
                'execution_time_ms': execution_time * 1000,
                'timestamp': datetime.now().isoformat(),
                'success': success
            })
            
            # Son 50 kaydı tut
            if len(self.performance_metrics['database_queries']) > 50:
                self.performance_metrics['database_queries'] = self.performance_metrics['database_queries'][-50:]
            
            # Slow query alert
            if execution_time > self.alert_thresholds['database_query_time_ms'] / 1000:
                self._send_alert('SLOW_QUERY', f"Slow database query: {execution_time:.2f}s")
                
        except Exception as e:
            self.logger.error(f"Database query tracking error: {e}")
    
    def track_cache_operation(self, operation, hit=True):
        """Cache operasyonunu izle"""
        try:
            if hit:
                self.performance_metrics['cache_hits'] += 1
            else:
                self.performance_metrics['cache_misses'] += 1
                
        except Exception as e:
            self.logger.error(f"Cache tracking error: {e}")
    
    def get_performance_summary(self):
        """Performans özetini al"""
        try:
            response_times = self.performance_metrics['response_times']
            memory_usage = self.performance_metrics['memory_usage']
            cpu_usage = self.performance_metrics['cpu_usage']
            database_queries = self.performance_metrics['database_queries']
            
            # Ortalama response time
            avg_response_time = 0
            if response_times:
                avg_response_time = sum(r['response_time_ms'] for r in response_times) / len(response_times)
            
            # Ortalama memory usage
            avg_memory_usage = 0
            if memory_usage:
                avg_memory_usage = sum(m['percent'] for m in memory_usage) / len(memory_usage)
            
            # Ortalama CPU usage
            avg_cpu_usage = 0
            if cpu_usage:
                avg_cpu_usage = sum(c['percent'] for c in cpu_usage) / len(cpu_usage)
            
            # Ortalama database query time
            avg_db_query_time = 0
            if database_queries:
                avg_db_query_time = sum(q['execution_time_ms'] for q in database_queries) / len(database_queries)
            
            # Error rate
            total_requests = len(response_times)
            error_count = sum(1 for r in response_times if not r['success'])
            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
            
            # Cache hit rate
            total_cache_operations = self.performance_metrics['cache_hits'] + self.performance_metrics['cache_misses']
            cache_hit_rate = (self.performance_metrics['cache_hits'] / total_cache_operations) * 100 if total_cache_operations > 0 else 0
            
            return {
                'avg_response_time_ms': round(avg_response_time, 2),
                'avg_memory_usage_percent': round(avg_memory_usage, 2),
                'avg_cpu_usage_percent': round(avg_cpu_usage, 2),
                'avg_db_query_time_ms': round(avg_db_query_time, 2),
                'error_rate_percent': round(error_rate, 2),
                'cache_hit_rate_percent': round(cache_hit_rate, 2),
                'total_requests': total_requests,
                'total_errors': error_count,
                'cache_hits': self.performance_metrics['cache_hits'],
                'cache_misses': self.performance_metrics['cache_misses'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Performance summary error: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_error_summary(self):
        """Hata özetini al"""
        try:
            error_counts = self.performance_metrics['error_counts']
            total_errors = sum(error_counts.values())
            
            return {
                'total_errors': total_errors,
                'error_breakdown': error_counts,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error summary error: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_health(self):
        """Sistem sağlık durumunu al"""
        try:
            # Sistem kaynakları
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Health score hesapla (0-100)
            health_score = 100
            
            # Memory health
            if memory.percent > 90:
                health_score -= 30
            elif memory.percent > 80:
                health_score -= 20
            elif memory.percent > 70:
                health_score -= 10
            
            # CPU health
            if cpu > 90:
                health_score -= 30
            elif cpu > 80:
                health_score -= 20
            elif cpu > 70:
                health_score -= 10
            
            # Disk health
            if disk.percent > 90:
                health_score -= 20
            elif disk.percent > 80:
                health_score -= 10
            
            # Error rate health
            response_times = self.performance_metrics['response_times']
            if response_times:
                total_requests = len(response_times)
                error_count = sum(1 for r in response_times if not r['success'])
                error_rate = (error_count / total_requests) * 100
                
                if error_rate > 10:
                    health_score -= 30
                elif error_rate > 5:
                    health_score -= 20
                elif error_rate > 2:
                    health_score -= 10
            
            # Health status
            if health_score >= 90:
                status = 'EXCELLENT'
            elif health_score >= 70:
                status = 'GOOD'
            elif health_score >= 50:
                status = 'WARNING'
            else:
                status = 'CRITICAL'
            
            return {
                'health_score': max(0, health_score),
                'status': status,
                'memory_percent': memory.percent,
                'cpu_percent': cpu,
                'disk_percent': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"System health error: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_metrics(self):
        """Metrikleri temizle"""
        try:
            self.performance_metrics = {
                'response_times': [],
                'error_counts': {},
                'memory_usage': [],
                'cpu_usage': [],
                'database_queries': [],
                'cache_hits': 0,
                'cache_misses': 0
            }
            self.logger.info("Performance metrics cleared")
            
        except Exception as e:
            self.logger.error(f"Clear metrics error: {e}")

# Global monitoring instance
monitoring_system = MonitoringSystem()

