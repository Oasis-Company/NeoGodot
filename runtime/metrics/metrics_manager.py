import time
import asyncio
import os
import psutil
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse


@dataclass
class LatencyStats:
    sum: float = 0.0
    count: int = 0
    min: float = float('inf')
    max: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0


@dataclass
class PerformanceSnapshot:
    timestamp: float
    cpu_percent: float
    memory_usage: int
    memory_percent: float
    request_count: int
    error_count: int
    avg_latency: float


class MetricsManager:
    def __init__(self, snapshot_interval: float = 60.0, max_snapshots: int = 1440):
        self.request_count: int = 0
        self.error_count: int = 0
        self.latency_samples: deque = deque(maxlen=10000)
        self.latency_stats: LatencyStats = LatencyStats()
        self.snapshots: deque = deque(maxlen=max_snapshots)
        self.snapshot_interval: float = snapshot_interval
        self._snapshot_task: Optional[asyncio.Task] = None
        self._start_time: float = time.time()
        self._process = psutil.Process(os.getpid())
        
        self._request_counts_by_endpoint: Dict[str, int] = {}
        self._error_counts_by_endpoint: Dict[str, int] = {}
        self._latencies_by_endpoint: Dict[str, deque] = {}

    def record_request(self, endpoint: str = "/") -> None:
        self.request_count += 1
        self._request_counts_by_endpoint[endpoint] = self._request_counts_by_endpoint.get(endpoint, 0) + 1

    def record_error(self, endpoint: str = "/") -> None:
        self.error_count += 1
        self._error_counts_by_endpoint[endpoint] = self._error_counts_by_endpoint.get(endpoint, 0) + 1

    def record_latency(self, latency_seconds: float, endpoint: str = "/") -> None:
        latency_ms = latency_seconds * 1000.0
        self.latency_samples.append(latency_ms)
        
        self.latency_stats.sum += latency_ms
        self.latency_stats.count += 1
        self.latency_stats.min = min(self.latency_stats.min, latency_ms)
        self.latency_stats.max = max(self.latency_stats.max, latency_ms)
        
        if endpoint not in self._latencies_by_endpoint:
            self._latencies_by_endpoint[endpoint] = deque(maxlen=1000)
        self._latencies_by_endpoint[endpoint].append(latency_ms)
        
        self._update_percentiles()

    def _update_percentiles(self) -> None:
        if not self.latency_samples:
            return
        
        sorted_latencies = sorted(self.latency_samples)
        n = len(sorted_latencies)
        
        self.latency_stats.p50 = sorted_latencies[int(n * 0.50)]
        self.latency_stats.p95 = sorted_latencies[int(n * 0.95)] if n > 20 else sorted_latencies[-1]
        self.latency_stats.p99 = sorted_latencies[int(n * 0.99)] if n > 100 else sorted_latencies[-1]

    def get_cpu_usage(self) -> float:
        return self._process.cpu_percent(interval=None)

    def get_memory_usage(self) -> Dict[str, Any]:
        mem_info = self._process.memory_info()
        return {
            "rss": mem_info.rss,
            "vms": mem_info.vms,
            "percent": self._process.memory_percent()
        }

    def get_error_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

    def get_avg_latency(self) -> float:
        if self.latency_stats.count == 0:
            return 0.0
        return self.latency_stats.sum / self.latency_stats.count

    def take_snapshot(self) -> PerformanceSnapshot:
        mem = self.get_memory_usage()
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=self.get_cpu_usage(),
            memory_usage=mem["rss"],
            memory_percent=mem["percent"],
            request_count=self.request_count,
            error_count=self.error_count,
            avg_latency=self.get_avg_latency()
        )
        self.snapshots.append(snapshot)
        return snapshot

    async def _snapshot_loop(self) -> None:
        while True:
            try:
                self.take_snapshot()
                await asyncio.sleep(self.snapshot_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(self.snapshot_interval)

    def start_snapshotting(self) -> None:
        if self._snapshot_task is None or self._snapshot_task.done():
            self._snapshot_task = asyncio.create_task(self._snapshot_loop())

    def stop_snapshotting(self) -> None:
        if self._snapshot_task and not self._snapshot_task.done():
            self._snapshot_task.cancel()

    def to_prometheus_format(self) -> str:
        lines: List[str] = []
        
        lines.append(f"# HELP neogodot_requests_total Total number of requests")
        lines.append(f"# TYPE neogodot_requests_total counter")
        lines.append(f"neogodot_requests_total {self.request_count}")
        
        lines.append(f"# HELP neogodot_errors_total Total number of errors")
        lines.append(f"# TYPE neogodot_errors_total counter")
        lines.append(f"neogodot_errors_total {self.error_count}")
        
        lines.append(f"# HELP neogodot_error_rate Error rate (0-1)")
        lines.append(f"# TYPE neogodot_error_rate gauge")
        lines.append(f"neogodot_error_rate {self.get_error_rate():.6f}")
        
        lines.append(f"# HELP neogodot_request_duration_seconds Request duration in seconds")
        lines.append(f"# TYPE neogodot_request_duration_seconds summary")
        avg_latency_sec = self.get_avg_latency() / 1000.0
        lines.append(f"neogodot_request_duration_seconds_sum {self.latency_stats.sum / 1000.0:.6f}")
        lines.append(f"neogodot_request_duration_seconds_count {self.latency_stats.count}")
        lines.append(f"neogodot_request_duration_seconds{{quantile=\"0.50\"}} {self.latency_stats.p50 / 1000.0:.6f}")
        lines.append(f"neogodot_request_duration_seconds{{quantile=\"0.95\"}} {self.latency_stats.p95 / 1000.0:.6f}")
        lines.append(f"neogodot_request_duration_seconds{{quantile=\"0.99\"}} {self.latency_stats.p99 / 1000.0:.6f}")
        
        lines.append(f"# HELP neogodot_cpu_percent CPU usage percentage")
        lines.append(f"# TYPE neogodot_cpu_percent gauge")
        lines.append(f"neogodot_cpu_percent {self.get_cpu_usage():.2f}")
        
        mem = self.get_memory_usage()
        lines.append(f"# HELP neogodot_memory_bytes Memory usage in bytes")
        lines.append(f"# TYPE neogodot_memory_bytes gauge")
        lines.append(f"neogodot_memory_bytes {mem['rss']}")
        
        lines.append(f"# HELP neogodot_memory_percent Memory usage percentage")
        lines.append(f"# TYPE neogodot_memory_percent gauge")
        lines.append(f"neogodot_memory_percent {mem['percent']:.2f}")
        
        lines.append(f"# HELP neogodot_uptime_seconds Service uptime in seconds")
        lines.append(f"# TYPE neogodot_uptime_seconds counter")
        lines.append(f"neogodot_uptime_seconds {time.time() - self._start_time:.0f}")
        
        for endpoint, count in self._request_counts_by_endpoint.items():
            lines.append(f"neogodot_requests_by_endpoint_total{{endpoint=\"{endpoint}\"}} {count}")
        
        for endpoint, count in self._error_counts_by_endpoint.items():
            lines.append(f"neogodot_errors_by_endpoint_total{{endpoint=\"{endpoint}\"}} {count}")
        
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        mem = self.get_memory_usage()
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.get_error_rate(),
            "latency": {
                "avg_ms": self.get_avg_latency(),
                "min_ms": self.latency_stats.min if self.latency_stats.min != float('inf') else 0.0,
                "max_ms": self.latency_stats.max,
                "p50_ms": self.latency_stats.p50,
                "p95_ms": self.latency_stats.p95,
                "p99_ms": self.latency_stats.p99,
                "sample_count": self.latency_stats.count
            },
            "cpu_percent": self.get_cpu_usage(),
            "memory": {
                "rss_bytes": mem["rss"],
                "vms_bytes": mem["vms"],
                "percent": mem["percent"]
            },
            "uptime_seconds": time.time() - self._start_time,
            "snapshots_count": len(self.snapshots)
        }


_metrics_manager: Optional[MetricsManager] = None


def get_metrics_manager(snapshot_interval: float = 60.0) -> MetricsManager:
    global _metrics_manager
    if _metrics_manager is None:
        _metrics_manager = MetricsManager(snapshot_interval=snapshot_interval)
    return _metrics_manager


metrics_router = APIRouter()


@metrics_router.get("/v1/metrics", response_class=PlainTextResponse)
async def get_metrics():
    manager = get_metrics_manager()
    return manager.to_prometheus_format()


@metrics_router.get("/v1/metrics/json")
async def get_metrics_json():
    manager = get_metrics_manager()
    return manager.get_stats()
