"""HTTP server for Prometheus metrics endpoint"""

import logging

from aiohttp import web
from prometheus_client import generate_latest

from ..collectors.manager import MetricsCollectorManager
from ..config import ExporterConfig

logger = logging.getLogger(__name__)


class PrometheusServer:
    """HTTP server for serving Prometheus metrics"""

    def __init__(self, config: ExporterConfig, collector_manager: MetricsCollectorManager):
        self.config = config
        self.collector_manager = collector_manager
        self.app = None
        self.runner = None
        self.site = None

    async def metrics_handler(self, _request):
        """HTTP handler for Prometheus metrics endpoint"""
        try:
            data = generate_latest()
            return web.Response(
                body=data,
                headers={"Content-Type": "text/plain; version=0.0.4; charset=utf-8"},
            )
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return web.Response(text="Error generating metrics", status=500)

    async def health_handler(self, _request):
        """Health check endpoint"""
        status = "healthy" if self.collector_manager.is_connected else "unhealthy"
        connection_status = "connected" if self.collector_manager.is_connected else "disconnected"

        info = {
            "status": status,
            "connection": connection_status,
            "router": self.config.hostname,
            "collection_interval": self.config.collection_interval,
        }

        response_text = f"Status: {status}\n" + "\n".join([f"{k}: {v}" for k, v in info.items()])
        return web.Response(text=response_text)

    async def info_handler(self, _request):
        """Info endpoint with metrics overview"""
        collector_info = self.collector_manager.get_collector_info()

        info_text = f"""ASUS Router Prometheus Exporter v2.0 (Modular)

Available Endpoints:
- /metrics       - Prometheus metrics
- /health        - Health check
- /info          - This information page
- /collectors    - Collector information

Configuration:
- Router: {self.config.hostname}
- Collection Interval: {self.config.collection_interval}s
- Log Level: {self.config.log_level}

Active Collectors:
"""
        for collector_name, data_types in collector_info.items():
            info_text += f"- {collector_name}: {', '.join(data_types)}\n"

        info_text += f"""
Total Data Types: {sum(len(types) for types in collector_info.values())}

Enhanced Features:
- Modular architecture with specialized collectors
- Individual client TX/RX rates in real-time
- Client RSSI values for WiFi connections
- Connection type classification (wired/wifi 2.4G/5G/6G)
- Internet access permission status per client
- Online/offline status tracking
- Detailed port capabilities and maximum rates
- Node-level port information for mesh networks
- Real-time client bandwidth utilization
- Comprehensive VPN metrics (OpenVPN, WireGuard, VPNC)
- System services and hardware monitoring
- Firmware update tracking and release notes
"""
        return web.Response(text=info_text, content_type="text/plain")

    async def collectors_handler(self, _request):
        """Collectors information endpoint"""
        collector_info = self.collector_manager.get_collector_info()

        collectors_text = "ASUS Router Exporter - Collector Information\n\n"

        for collector_name, data_types in collector_info.items():
            collectors_text += f"{collector_name}:\n"
            for data_type in data_types:
                collectors_text += f"  - {data_type}\n"
            collectors_text += "\n"

        collectors_text += f"Total Collectors: {len(collector_info)}\n"
        collectors_text += (
            f"Total Data Types: {sum(len(types) for types in collector_info.values())}\n"
        )

        return web.Response(text=collectors_text, content_type="text/plain")

    async def start_server(self):
        """Start the HTTP server"""
        self.app = web.Application()
        self.app.router.add_get("/metrics", self.metrics_handler)
        self.app.router.add_get("/health", self.health_handler)
        self.app.router.add_get("/info", self.info_handler)
        self.app.router.add_get("/collectors", self.collectors_handler)
        self.app.router.add_get("/", self.info_handler)

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "0.0.0.0", self.config.port)
        await self.site.start()

        logger.info(f"Prometheus exporter started on port {self.config.port}")
        logger.info(f"Metrics available at: http://0.0.0.0:{self.config.port}/metrics")

    async def stop_server(self):
        """Stop the HTTP server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
