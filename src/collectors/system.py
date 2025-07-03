"""System metrics collector (CPU, Memory, Load Average)"""

from typing import Any, Dict

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    ACTIVE_CONNECTIONS,
    COLLECTION_ERRORS_TOTAL,
    CPU_USAGE,
    JFFS_FREE,
    JFFS_TOTAL,
    JFFS_USED,
    LOAD_AVERAGE,
    NVRAM_USED,
    RAM_BUFFERS,
    RAM_CACHE,
    RAM_FREE,
    RAM_SWAP1,
    RAM_SWAP2,
    RAM_TOTAL,
    RAM_USAGE_PERCENT,
    RAM_USED,
    TOTAL_CONNECTIONS,
)
from .base import BaseCollector


class SystemCollector(BaseCollector):
    """Collects system metrics including CPU, RAM, and system info"""

    def get_data_types(self) -> list[AsusData]:
        return [AsusData.CPU, AsusData.RAM, AsusData.SYSINFO]

    async def collect(self) -> Dict[str, Any]:
        """Collect system metrics"""
        metrics = {}

        try:
            await self._collect_cpu_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect CPU data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="cpu").inc()

        try:
            await self._collect_memory_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect memory data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="memory").inc()

        try:
            await self._collect_sysinfo_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect sysinfo data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="sysinfo").inc()

        return metrics

    async def _collect_cpu_metrics(self, metrics: Dict[str, Any]):
        """Collect CPU metrics"""
        cpu_data = await self.router.async_get_data(AsusData.CPU)
        if cpu_data:
            self.logger.debug(f"CPU data structure: {cpu_data}")

            # Handle different possible CPU data structures
            cpu_usage = None
            if isinstance(cpu_data, dict):
                cpu_usage = (
                    cpu_data.get("usage")
                    or cpu_data.get("cpu_usage")
                    or cpu_data.get("percent")
                )
            elif isinstance(cpu_data, (int, float)):
                cpu_usage = cpu_data

            if cpu_usage is not None:
                try:
                    cpu_value = float(cpu_usage)
                    CPU_USAGE.set(cpu_value)
                    metrics["cpu_usage"] = cpu_value
                    self.logger.debug(f"CPU usage: {cpu_value}%")
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Error parsing CPU usage: {e}")
            else:
                self.logger.warning(f"No CPU usage found in data: {cpu_data}")

    async def _collect_memory_metrics(self, metrics: Dict[str, Any]):
        """Collect RAM and memory metrics"""
        ram_data = await self.router.async_get_data(AsusData.RAM)
        if ram_data:
            if "used" in ram_data:
                RAM_USED.set(float(ram_data["used"]))
                metrics["ram_used"] = ram_data["used"]
            if "free" in ram_data:
                RAM_FREE.set(float(ram_data["free"]))
                metrics["ram_free"] = ram_data["free"]
            if "total" in ram_data:
                RAM_TOTAL.set(float(ram_data["total"]))
                metrics["ram_total"] = ram_data["total"]
            if "usage" in ram_data:
                RAM_USAGE_PERCENT.set(float(ram_data["usage"]))
                metrics["ram_usage_percent"] = ram_data["usage"]

            self.logger.debug(
                f"RAM - Used: {ram_data.get('used', 'N/A')}, Free: {ram_data.get('free', 'N/A')}"
            )

    async def _collect_sysinfo_metrics(self, metrics: Dict[str, Any]):
        """Collect system information metrics"""
        sysinfo_data = await self.router.async_get_data(AsusData.SYSINFO)
        if sysinfo_data:
            # Connection stats
            connections = sysinfo_data.get("connections", {})
            if "total" in connections:
                TOTAL_CONNECTIONS.set(connections["total"])
                metrics["total_connections"] = connections["total"]
            if "active" in connections:
                ACTIVE_CONNECTIONS.set(connections["active"])
                metrics["active_connections"] = connections["active"]

            # Memory details
            memory = sysinfo_data.get("memory", {})
            for key, metric in [
                ("buffers", RAM_BUFFERS),
                ("cache", RAM_CACHE),
                ("swap_1", RAM_SWAP1),
                ("swap_2", RAM_SWAP2),
                ("nvram", NVRAM_USED),
                ("jffs_free", JFFS_FREE),
                ("jffs_used", JFFS_USED),
                ("jffs_total", JFFS_TOTAL),
            ]:
                if key in memory and memory[key] is not None:
                    metric.set(float(memory[key]))
                    metrics[f"memory_{key}"] = memory[key]

            # Load average
            load_avg = sysinfo_data.get("load_avg", {})
            for period in [1, 5, 15]:
                if period in load_avg:
                    LOAD_AVERAGE.labels(period=f"{period}m").set(
                        float(load_avg[period])
                    )
                    metrics[f"load_avg_{period}m"] = load_avg[period]

            self.logger.debug("Collected system info metrics")
