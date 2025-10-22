"""Collector manager to coordinate all metric collection"""

import asyncio
import logging
from typing import Any

from asusrouter import AsusRouter

from ..metrics.prometheus_metrics import (
    COLLECTION_ERRORS_TOTAL,
    CONNECTION_STATUS,
    LAST_COLLECTION_TIMESTAMP,
    collection_time,
)
from .base import BaseCollector
from .devices import DeviceInventoryCollector
from .firmware import FirmwareCollector
from .hardware import HardwareCollector
from .network import NetworkCollector
from .services import ServicesCollector
from .system import SystemCollector
from .vpn import VPNCollector
from .wifi import WiFiCollector

logger = logging.getLogger(__name__)


class MetricsCollectorManager:
    """Manages all metric collectors and coordinates collection"""

    def __init__(self, router: AsusRouter):
        self.router = router
        self.collectors: list[BaseCollector] = [
            SystemCollector(router),
            NetworkCollector(router),
            WiFiCollector(router),
            HardwareCollector(router),
            FirmwareCollector(router),
            VPNCollector(router),
            ServicesCollector(router),
            DeviceInventoryCollector(router),
        ]
        self.is_connected = False
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect_router(self) -> None:
        """Connect to the ASUS router"""
        try:
            await self.router.async_connect()
            self.is_connected = True
            CONNECTION_STATUS.set(1)
            self.logger.info("Successfully connected to router")
        except Exception as e:
            self.is_connected = False
            CONNECTION_STATUS.set(0)
            self.logger.error(f"Failed to connect to router: {e}")
            raise

    @collection_time.time()
    async def collect_all_metrics(self) -> dict[str, Any]:
        """Collect metrics from all collectors"""
        if not self.router or not self.is_connected:
            self.logger.warning("Router not connected, attempting to reconnect...")
            try:
                await self.connect_router()
            except Exception:
                COLLECTION_ERRORS_TOTAL.labels(error_type="connection").inc()
                return {}

        all_metrics = {}

        try:
            # Collect metrics from all collectors concurrently
            collection_tasks = [collector.collect() for collector in self.collectors]

            results = await asyncio.gather(*collection_tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                collector_name = self.collectors[i].__class__.__name__

                if isinstance(result, Exception):
                    self.logger.error(f"Error in {collector_name}: {result}")
                    COLLECTION_ERRORS_TOTAL.labels(error_type=collector_name.lower()).inc()
                elif isinstance(result, dict):
                    all_metrics.update(result)
                    self.logger.debug(f"Collected {len(result)} metrics from {collector_name}")

            CONNECTION_STATUS.set(1)
            LAST_COLLECTION_TIMESTAMP.set_to_current_time()
            self.logger.debug(f"Successfully collected {len(all_metrics)} total metrics")

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            self.is_connected = False
            CONNECTION_STATUS.set(0)
            COLLECTION_ERRORS_TOTAL.labels(error_type="general").inc()

        return all_metrics

    def get_collector_info(self) -> dict[str, list[str]]:
        """Get information about all collectors and their data types"""
        info = {}
        for collector in self.collectors:
            collector_name = collector.__class__.__name__
            data_types = [dt.value for dt in collector.get_data_types()]
            info[collector_name] = data_types
        return info
