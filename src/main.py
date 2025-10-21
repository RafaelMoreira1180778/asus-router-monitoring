"""Main exporter application"""

import asyncio
import contextlib
import logging
import sys

from asusrouter import AsusRouter
from asusrouter.connection_config import ARConnectionConfig, ARConnectionConfigKey

from .collectors import MetricsCollectorManager
from .config import ExporterConfig, setup_logging
from .server import PrometheusServer

logger = logging.getLogger(__name__)


class AsusExporter:
    """Main ASUS Router Prometheus Exporter application"""

    def __init__(self, config: ExporterConfig):
        self.config = config
        self.router = None
        self.collector_manager = None
        self.server = None
        self.collection_task = None

    async def initialize(self):
        """Initialize the exporter components"""
        # Setup connection configuration with resilience (v1.19.0+)
        connection_config = ARConnectionConfig()
        connection_config.set(ARConnectionConfigKey.ALLOW_FALLBACK, self.config.allow_fallback)
        connection_config.set(ARConnectionConfigKey.STRICT_SSL, self.config.strict_ssl)
        connection_config.set(
            ARConnectionConfigKey.ALLOW_UPGRADE_HTTP_TO_HTTPS,
            self.config.allow_upgrade_http_to_https,
        )

        # Setup router connection with resilience
        self.router = AsusRouter(
            hostname=self.config.hostname,
            username=self.config.username,
            password=self.config.password,
            use_ssl=self.config.use_ssl,
            connection_config=connection_config,
        )

        # Setup collector manager
        self.collector_manager = MetricsCollectorManager(self.router)

        # Setup HTTP server
        self.server = PrometheusServer(self.config, self.collector_manager)

        logger.info(f"Exporter initialized for router: {self.config.hostname}")
        logger.info(
            f"Connection resilience enabled: fallback={self.config.allow_fallback}, strict_ssl={self.config.strict_ssl}"
        )

    async def start(self):
        """Start the exporter"""
        if not self.collector_manager or not self.server:
            await self.initialize()

        logger.info("Starting ASUS Router Prometheus Exporter v2.0")
        logger.info(f"Target router: {self.config.hostname}")
        logger.info(f"Collection interval: {self.config.collection_interval}s")

        # Connect to router
        await self.collector_manager.connect_router()

        # Start HTTP server
        await self.server.start_server()

        # Start metrics collection loop
        self.collection_task = asyncio.create_task(self._metrics_collection_loop())

        logger.info("Exporter started successfully")

    async def stop(self):
        """Stop the exporter"""
        logger.info("Stopping exporter...")

        if self.collection_task:
            self.collection_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.collection_task

        if self.server:
            await self.server.stop_server()

        if self.router:
            await self.router.async_disconnect()

        logger.info("Exporter stopped")

    async def _metrics_collection_loop(self):
        """Main loop for collecting metrics"""
        while True:
            try:
                await self.collector_manager.collect_all_metrics()
                await asyncio.sleep(self.config.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(self.config.collection_interval * 2)  # Wait longer on error

    async def run_forever(self):
        """Run the exporter until interrupted"""
        try:
            await self.start()
            # Keep the exporter running
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.stop()


async def main():
    """Main entry point"""
    try:
        # Load configuration
        config = ExporterConfig.from_env()

        # Setup logging
        setup_logging(config.log_level)

        # Create and run exporter
        exporter = AsusExporter(config)
        await exporter.run_forever()

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nUsage:")
        print("Set environment variables:")
        print("  ASUS_HOSTNAME=192.168.1.1 (default)")
        print("  ASUS_USERNAME=admin (default)")
        print("  ASUS_PASSWORD=your_password (required)")
        print("  ASUS_USE_SSL=false (default)")
        print("  EXPORTER_PORT=8000 (default)")
        print("  EXPORTER_COLLECTION_INTERVAL=15 (default)")
        print("  EXPORTER_LOG_LEVEL=INFO (default)")
        print("\nExample:")
        print("  ASUS_PASSWORD=mypassword python3 -m src.main")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Exporter failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
