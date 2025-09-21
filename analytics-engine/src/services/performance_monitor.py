"""
Performance monitoring service for the Analytics Engine.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import psutil
from loguru import logger

from .cache_service import cache_service


class PerformanceMonitor:
    """Monitor system and application performance."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'cpu_percent': [],
            'memory_percent': [],
            'disk_io_read': [],
            'disk_io_write': [],
            'network_io_sent': [],
            'network_io_recv': [],
            'request_count': [],
            'request_duration': [],
            'cache_hits': [],
            'cache_misses': []
        }
        self.start_time = time.time()
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.monitoring = False
    
    async def start_monitoring(self, interval: int = 60):
        """Start performance monitoring."""
        self.monitoring = True
        logger.info("Performance monitoring started")
        
        while self.monitoring:
            try:
                await self._collect_system_metrics()
                await self._collect_application_metrics()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        logger.info("Performance monitoring stopped")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_percent'].append(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_percent'].append(memory.percent)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.metrics['disk_io_read'].append(disk_io.read_bytes)
                self.metrics['disk_io_write'].append(disk_io.write_bytes)
            
            # Network I/O
            network_io = psutil.net_io_counters()
            if network_io:
                self.metrics['network_io_sent'].append(network_io.bytes_sent)
                self.metrics['network_io_recv'].append(network_io.bytes_recv)
            
            # Keep only last 100 measurements
            for key in self.metrics:
                if len(self.metrics[key]) > 100:
                    self.metrics[key] = self.metrics[key][-100:]
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _collect_application_metrics(self):
        """Collect application-specific metrics."""
        try:
            # Request metrics
            self.metrics['request_count'].append(self.request_count)
            
            # Cache metrics
            self.metrics['cache_hits'].append(self.cache_hits)
            self.metrics['cache_misses'].append(self.cache_misses)
            
            # Store metrics in cache for API access
            metrics_summary = await self.get_metrics_summary()
            await cache_service.set(
                "performance:metrics",
                metrics_summary,
                expiration=timedelta(minutes=5)
            )
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    def record_request(self, duration: float):
        """Record a request and its duration."""
        self.request_count += 1
        self.metrics['request_duration'].append(duration)
        
        # Keep only last 1000 request durations
        if len(self.metrics['request_duration']) > 1000:
            self.metrics['request_duration'] = self.metrics['request_duration'][-1000:]
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    async def get_metrics_summary(self) -> Dict:
        """Get a summary of current metrics."""
        try:
            current_time = datetime.utcnow()
            uptime = time.time() - self.start_time
            
            # Calculate averages and current values
            summary = {
                'timestamp': current_time.isoformat(),
                'uptime_seconds': uptime,
                'system': {
                    'cpu_percent': self._get_metric_stats('cpu_percent'),
                    'memory_percent': self._get_metric_stats('memory_percent'),
                    'disk_io': {
                        'read_bytes': self._get_latest_metric('disk_io_read'),
                        'write_bytes': self._get_latest_metric('disk_io_write')
                    },
                    'network_io': {
                        'sent_bytes': self._get_latest_metric('network_io_sent'),
                        'recv_bytes': self._get_latest_metric('network_io_recv')
                    }
                },
                'application': {
                    'total_requests': self.request_count,
                    'requests_per_minute': self._calculate_requests_per_minute(),
                    'average_request_duration': self._get_metric_stats('request_duration'),
                    'cache': {
                        'hits': self.cache_hits,
                        'misses': self.cache_misses,
                        'hit_rate': self._calculate_cache_hit_rate()
                    }
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return {}
    
    def _get_metric_stats(self, metric_name: str) -> Dict:
        """Get statistics for a metric."""
        values = self.metrics.get(metric_name, [])
        
        if not values:
            return {'current': 0, 'average': 0, 'min': 0, 'max': 0}
        
        return {
            'current': values[-1] if values else 0,
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values)
        }
    
    def _get_latest_metric(self, metric_name: str) -> float:
        """Get the latest value for a metric."""
        values = self.metrics.get(metric_name, [])
        return values[-1] if values else 0
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute."""
        if len(self.metrics['request_count']) < 2:
            return 0
        
        # Get requests in last minute (assuming 60-second intervals)
        recent_requests = self.metrics['request_count'][-2:]
        return recent_requests[-1] - recent_requests[0] if len(recent_requests) >= 2 else 0
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_cache_operations = self.cache_hits + self.cache_misses
        
        if total_cache_operations == 0:
            return 0
        
        return (self.cache_hits / total_cache_operations) * 100
    
    async def get_health_status(self) -> Dict:
        """Get system health status."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine health status based on thresholds
            health_status = "healthy"
            issues = []
            
            if cpu_percent > 80:
                health_status = "warning"
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 85:
                health_status = "warning"
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 90:
                health_status = "critical"
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            if cpu_percent > 95 or memory.percent > 95:
                health_status = "critical"
            
            return {
                'status': health_status,
                'timestamp': datetime.utcnow().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk.percent,
                    'available_memory_gb': memory.available / (1024**3)
                },
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
