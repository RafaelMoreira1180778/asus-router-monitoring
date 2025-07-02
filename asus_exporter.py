#!/usr/bin/env python3
"""
ASUS Router Prometheus Exporter

This script creates a comprehensive Prometheus exporter that fetches metrics from ASUS routers
using the AsusRouter library and exposes them in Prometheus format.
"""

import asyncio
import logging
import os
import sys
from typing import Optional

from aiohttp import web
from asusrouter import AsusData, AsusRouter
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

# Configure logging
log_level = os.getenv("EXPORTER_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Collection timing
collection_time = Histogram(
    "asus_collection_duration_seconds", "Time spent collecting metrics from router"
)

# System metrics
CPU_USAGE = Gauge("asus_cpu_usage_percent", "CPU usage percentage")
LOAD_AVERAGE = Gauge("asus_load_average", "System load average", ["period"])

# Memory metrics
RAM_USED = Gauge("asus_ram_used_bytes", "RAM used in bytes")
RAM_FREE = Gauge("asus_ram_free_bytes", "RAM free in bytes")
RAM_TOTAL = Gauge("asus_ram_total_bytes", "RAM total in bytes")
RAM_USAGE_PERCENT = Gauge("asus_ram_usage_percent", "RAM usage percentage")
RAM_BUFFERS = Gauge("asus_ram_buffers_bytes", "RAM buffers in bytes")
RAM_CACHE = Gauge("asus_ram_cache_bytes", "RAM cache in bytes")
RAM_SWAP1 = Gauge("asus_ram_swap1_bytes", "RAM swap1 in bytes")
RAM_SWAP2 = Gauge("asus_ram_swap2_bytes", "RAM swap2 in bytes")
NVRAM_USED = Gauge("asus_nvram_used_bytes", "NVRAM used in bytes")
JFFS_FREE = Gauge("asus_jffs_free_megabytes", "JFFS free space in MB")
JFFS_USED = Gauge("asus_jffs_used_megabytes", "JFFS used space in MB")
JFFS_TOTAL = Gauge("asus_jffs_total_megabytes", "JFFS total space in MB")

# Network interface metrics - WAN
WAN_RX_BYTES = Counter("asus_wan_rx_bytes_total", "WAN RX bytes total")
WAN_TX_BYTES = Counter("asus_wan_tx_bytes_total", "WAN TX bytes total")
WAN_RX_RATE = Gauge("asus_wan_rx_rate_bytes_per_sec", "WAN RX rate in bytes per second")
WAN_TX_RATE = Gauge("asus_wan_tx_rate_bytes_per_sec", "WAN TX rate in bytes per second")

# Network interface metrics - LAN/WiFi
INTERFACE_RX_BYTES = Counter(
    "asus_interface_rx_bytes_total", "Interface RX bytes total", ["interface"]
)
INTERFACE_TX_BYTES = Counter(
    "asus_interface_tx_bytes_total", "Interface TX bytes total", ["interface"]
)

# Port metrics
PORT_STATUS = Gauge(
    "asus_port_status", "Port status (1=up, 0=down)", ["port_type", "port_id"]
)
PORT_LINK_RATE = Gauge(
    "asus_port_link_rate_mbps", "Port link rate in Mbps", ["port_type", "port_id"]
)

# Temperature metrics
TEMPERATURE = Gauge("asus_temperature_celsius", "Temperature in Celsius", ["sensor"])

# WiFi client metrics
WIFI_CLIENTS_TOTAL = Gauge("asus_wifi_clients_total", "Total number of WiFi clients")
WIFI_CLIENTS_BY_BAND = Gauge(
    "asus_wifi_clients_by_band", "Number of WiFi clients by band", ["band"]
)
WIFI_CLIENTS_ASSOCIATED = Gauge(
    "asus_wifi_clients_associated", "WiFi clients associated", ["band"]
)
WIFI_CLIENTS_AUTHORIZED = Gauge(
    "asus_wifi_clients_authorized", "WiFi clients authorized", ["band"]
)
WIFI_CLIENTS_AUTHENTICATED = Gauge(
    "asus_wifi_clients_authenticated", "WiFi clients authenticated", ["band"]
)

# Connection metrics
CONNECTION_STATUS = Gauge(
    "asus_connection_status", "Router connection status (1=connected, 0=disconnected)"
)
TOTAL_CONNECTIONS = Gauge("asus_connections_total", "Total network connections")
ACTIVE_CONNECTIONS = Gauge("asus_connections_active", "Active network connections")

# System info
ROUTER_INFO = Info("asus_router", "Router information")
BOOTTIME = Gauge("asus_boot_timestamp_seconds", "Router boot timestamp")

# Firmware info
FIRMWARE_INFO = Info("asus_firmware", "Firmware information")
FIRMWARE_UPDATE_AVAILABLE = Gauge(
    "asus_firmware_update_available", "Firmware update available (1=yes, 0=no)"
)

# VPN metrics
OPENVPN_CLIENT_STATUS = Gauge(
    "asus_openvpn_client_status", "OpenVPN client status", ["client_id"]
)
OPENVPN_SERVER_STATUS = Gauge(
    "asus_openvpn_server_status", "OpenVPN server status", ["server_id"]
)
WIREGUARD_CLIENT_STATUS = Gauge(
    "asus_wireguard_client_status", "WireGuard client status", ["client_id"]
)
WIREGUARD_SERVER_STATUS = Gauge(
    "asus_wireguard_server_status", "WireGuard server status", ["server_id"]
)

# LED and Aura metrics
LED_STATUS = Gauge("asus_led_status", "LED status (1=on, 0=off)")
AURA_STATUS = Gauge("asus_aura_status", "Aura lighting status")

# Collection metrics
LAST_COLLECTION_TIMESTAMP = Gauge(
    "asus_last_collection_timestamp_seconds", "Timestamp of last successful collection"
)
COLLECTION_ERRORS_TOTAL = Counter(
    "asus_collection_errors_total", "Total collection errors", ["error_type"]
)


class AsusExporter:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        use_ssl: bool = False,
        port: int = 8000,
        collection_interval: int = 15,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.port = port
        self.collection_interval = collection_interval
        self.router: Optional[AsusRouter] = None
        self.is_connected = False

    async def connect_router(self):
        """Connect to the ASUS router"""
        try:
            self.router = AsusRouter(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                use_ssl=self.use_ssl,
            )
            await self.router.async_connect()
            self.is_connected = True
            CONNECTION_STATUS.set(1)
            logger.info(f"Successfully connected to router at {self.hostname}")

            # Set router info
            try:
                info = await self.router.async_get_data(AsusData.DEVICEMAP)
                if info:
                    router_info = {
                        "model": str(info.get("model", "unknown")),
                        "firmware": str(info.get("firmware", "unknown")),
                        "hostname": self.hostname,
                        "brand": str(info.get("brand", "ASUSTek")),
                    }
                    ROUTER_INFO.info(router_info)
                    logger.info(
                        f"Router model: {router_info['model']}, firmware: {router_info['firmware']}"
                    )

                # Set boot time if available
                boot_data = await self.router.async_get_data(AsusData.BOOTTIME)
                if boot_data and "timestamp" in boot_data:
                    BOOTTIME.set(boot_data["timestamp"])

            except Exception as e:
                logger.warning(f"Could not fetch router info: {e}")

        except Exception as e:
            self.is_connected = False
            CONNECTION_STATUS.set(0)
            logger.error(f"Failed to connect to router: {e}")
            raise

    @collection_time.time()
    async def collect_metrics(self):
        """Collect all available metrics from the router"""
        if not self.router or not self.is_connected:
            logger.warning("Router not connected, attempting to reconnect...")
            try:
                await self.connect_router()
            except Exception:
                COLLECTION_ERRORS_TOTAL.labels(error_type="connection").inc()
                return

        try:
            # Collect CPU and system metrics
            await self._collect_cpu_metrics()

            # Collect memory metrics
            await self._collect_memory_metrics()

            # Collect system info metrics
            await self._collect_sysinfo_metrics()

            # Collect network metrics
            await self._collect_network_metrics()

            # Collect WAN metrics
            await self._collect_wan_metrics()

            # Collect port metrics
            await self._collect_port_metrics()

            # Collect temperature metrics
            await self._collect_temperature_metrics()

            # Collect WiFi client metrics
            await self._collect_wifi_metrics()

            # Collect firmware metrics
            await self._collect_firmware_metrics()

            # Collect VPN metrics
            await self._collect_vpn_metrics()

            # Collect LED metrics
            await self._collect_led_metrics()

            CONNECTION_STATUS.set(1)
            LAST_COLLECTION_TIMESTAMP.set_to_current_time()
            logger.debug("Successfully collected all available metrics")

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            self.is_connected = False
            CONNECTION_STATUS.set(0)
            COLLECTION_ERRORS_TOTAL.labels(error_type="general").inc()

    async def _collect_cpu_metrics(self):
        """Collect CPU metrics"""
        try:
            cpu_data = await self.router.async_get_data(AsusData.CPU)
            if cpu_data and "usage" in cpu_data:
                CPU_USAGE.set(float(cpu_data["usage"]))
                logger.debug(f"CPU usage: {cpu_data['usage']}%")
        except Exception as e:
            logger.debug(f"Failed to collect CPU data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="cpu").inc()

    async def _collect_memory_metrics(self):
        """Collect RAM and memory metrics"""
        try:
            ram_data = await self.router.async_get_data(AsusData.RAM)
            if ram_data:
                if "used" in ram_data:
                    RAM_USED.set(float(ram_data["used"]))
                if "free" in ram_data:
                    RAM_FREE.set(float(ram_data["free"]))
                if "total" in ram_data:
                    RAM_TOTAL.set(float(ram_data["total"]))
                if "usage" in ram_data:
                    RAM_USAGE_PERCENT.set(float(ram_data["usage"]))

                logger.debug(
                    f"RAM - Used: {ram_data.get('used', 'N/A')}, Free: {ram_data.get('free', 'N/A')}"
                )
        except Exception as e:
            logger.debug(f"Failed to collect RAM data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="memory").inc()

    async def _collect_sysinfo_metrics(self):
        """Collect system information metrics"""
        try:
            sysinfo_data = await self.router.async_get_data(AsusData.SYSINFO)
            if sysinfo_data:
                # Connection stats
                connections = sysinfo_data.get("connections", {})
                if "total" in connections:
                    TOTAL_CONNECTIONS.set(connections["total"])
                if "active" in connections:
                    ACTIVE_CONNECTIONS.set(connections["active"])

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

                # Load average
                load_avg = sysinfo_data.get("load_avg", {})
                for period in [1, 5, 15]:
                    if period in load_avg:
                        LOAD_AVERAGE.labels(period=f"{period}m").set(
                            float(load_avg[period])
                        )

                # WiFi client details by band
                wlan = sysinfo_data.get("wlan", {})
                for band, stats in wlan.items():
                    if isinstance(stats, dict):
                        band_name = str(band)
                        for metric_name, metric_gauge in [
                            ("client_associated", WIFI_CLIENTS_ASSOCIATED),
                            ("client_authorized", WIFI_CLIENTS_AUTHORIZED),
                            ("client_authenticated", WIFI_CLIENTS_AUTHENTICATED),
                        ]:
                            if metric_name in stats:
                                metric_gauge.labels(band=band_name).set(
                                    float(stats[metric_name])
                                )

                logger.debug("Collected system info metrics")
        except Exception as e:
            logger.debug(f"Failed to collect sysinfo data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="sysinfo").inc()

    async def _collect_network_metrics(self):
        """Collect network interface metrics"""
        try:
            network_data = await self.router.async_get_data(AsusData.NETWORK)
            if network_data:
                for interface, stats in network_data.items():
                    if isinstance(stats, dict) and "rx" in stats and "tx" in stats:
                        interface_name = str(interface)
                        INTERFACE_RX_BYTES.labels(
                            interface=interface_name
                        )._value._value = float(stats["rx"])
                        INTERFACE_TX_BYTES.labels(
                            interface=interface_name
                        )._value._value = float(stats["tx"])

                logger.debug("Collected network interface metrics")
        except Exception as e:
            logger.debug(f"Failed to collect network data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="network").inc()

    async def _collect_wan_metrics(self):
        """Collect WAN metrics"""
        try:
            wan_data = await self.router.async_get_data(AsusData.WAN)
            if wan_data:
                if "rx_bytes" in wan_data:
                    WAN_RX_BYTES._value._value = float(wan_data["rx_bytes"])
                if "tx_bytes" in wan_data:
                    WAN_TX_BYTES._value._value = float(wan_data["tx_bytes"])
                if "rx_rate" in wan_data:
                    WAN_RX_RATE.set(float(wan_data["rx_rate"]))
                if "tx_rate" in wan_data:
                    WAN_TX_RATE.set(float(wan_data["tx_rate"]))

                logger.debug(
                    f"WAN - RX: {wan_data.get('rx_bytes', 'N/A')}, TX: {wan_data.get('tx_bytes', 'N/A')}"
                )
        except Exception as e:
            logger.debug(f"Failed to collect WAN data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="wan").inc()

    async def _collect_port_metrics(self):
        """Collect port status metrics"""
        try:
            ports_data = await self.router.async_get_data(AsusData.PORTS)
            if ports_data:
                for port_type, ports in ports_data.items():
                    if isinstance(ports, dict):
                        port_type_name = str(port_type)
                        for port_id, port_info in ports.items():
                            if isinstance(port_info, dict):
                                port_id_str = str(port_id)

                                # Port status
                                if "state" in port_info:
                                    PORT_STATUS.labels(
                                        port_type=port_type_name, port_id=port_id_str
                                    ).set(1 if port_info["state"] else 0)

                                # Link rate
                                if "link_rate" in port_info:
                                    # Convert enum values to numeric if needed
                                    link_rate = port_info["link_rate"]
                                    if hasattr(link_rate, "value"):
                                        link_rate = link_rate.value
                                    elif isinstance(link_rate, str):
                                        # Parse common link rate strings
                                        rate_map = {
                                            "LINK_10": 10,
                                            "LINK_100": 100,
                                            "LINK_1000": 1000,
                                            "LINK_2500": 2500,
                                            "LINK_5000": 5000,
                                            "LINK_10000": 10000,
                                            "LINK_DOWN": 0,
                                        }
                                        link_rate = rate_map.get(link_rate, 0)

                                    PORT_LINK_RATE.labels(
                                        port_type=port_type_name, port_id=port_id_str
                                    ).set(float(link_rate))

                logger.debug("Collected port metrics")
        except Exception as e:
            logger.debug(f"Failed to collect port data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="ports").inc()

    async def _collect_temperature_metrics(self):
        """Collect temperature metrics"""
        try:
            temp_data = await self.router.async_get_data(AsusData.TEMPERATURE)
            if temp_data:
                for sensor, temp in temp_data.items():
                    if isinstance(temp, (int, float)):
                        sensor_name = str(sensor)
                        TEMPERATURE.labels(sensor=sensor_name).set(float(temp))

                logger.debug(f"Temperature data: {temp_data}")
        except Exception as e:
            logger.debug(f"Failed to collect temperature data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="temperature").inc()

    async def _collect_wifi_metrics(self):
        """Collect WiFi client metrics"""
        try:
            wifi_data = await self.router.async_get_data(AsusData.CLIENTS)
            if wifi_data:
                total_clients = len(wifi_data)
                WIFI_CLIENTS_TOTAL.set(total_clients)

                # Count clients by band if available
                bands = {}
                for client in wifi_data.values():
                    if isinstance(client, dict) and "band" in client:
                        band = str(client["band"])
                        bands[band] = bands.get(band, 0) + 1

                for band, count in bands.items():
                    WIFI_CLIENTS_BY_BAND.labels(band=band).set(count)

                logger.debug(f"WiFi clients: total={total_clients}, by band={bands}")
        except Exception as e:
            logger.debug(f"Failed to collect WiFi client data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="wifi").inc()

    async def _collect_firmware_metrics(self):
        """Collect firmware metrics"""
        try:
            firmware_data = await self.router.async_get_data(AsusData.FIRMWARE)
            if firmware_data:
                # Firmware info
                if "current" in firmware_data:
                    FIRMWARE_INFO.info(
                        {
                            "current": str(firmware_data.get("current", "unknown")),
                            "available": str(firmware_data.get("available", "none")),
                            "state": str(firmware_data.get("state", "unknown")),
                        }
                    )

                # Update availability
                if "state" in firmware_data:
                    FIRMWARE_UPDATE_AVAILABLE.set(1 if firmware_data["state"] else 0)

                logger.debug("Collected firmware metrics")
        except Exception as e:
            logger.debug(f"Failed to collect firmware data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="firmware").inc()

    async def _collect_vpn_metrics(self):
        """Collect VPN metrics"""
        try:
            # OpenVPN metrics
            try:
                openvpn_data = await self.router.async_get_data(AsusData.OPENVPN)
                if openvpn_data:
                    # Client metrics
                    clients = openvpn_data.get("client", {})
                    for client_id, client_info in clients.items():
                        if isinstance(client_info, dict) and "state" in client_info:
                            state_value = client_info["state"]
                            # Convert enum to numeric if needed
                            if hasattr(state_value, "value"):
                                state_value = state_value.value
                            OPENVPN_CLIENT_STATUS.labels(client_id=str(client_id)).set(
                                state_value
                            )

                    # Server metrics
                    servers = openvpn_data.get("server", {})
                    for server_id, server_info in servers.items():
                        if isinstance(server_info, dict) and "state" in server_info:
                            state_value = server_info["state"]
                            if hasattr(state_value, "value"):
                                state_value = state_value.value
                            OPENVPN_SERVER_STATUS.labels(server_id=str(server_id)).set(
                                state_value
                            )

                    logger.debug("Collected OpenVPN metrics")
            except Exception as e:
                logger.debug(f"OpenVPN metrics not available: {e}")

            # WireGuard metrics
            try:
                wg_data = await self.router.async_get_data(AsusData.WIREGUARD)
                if wg_data:
                    # Process WireGuard data similar to OpenVPN
                    logger.debug("Collected WireGuard metrics")
            except Exception as e:
                logger.debug(f"WireGuard metrics not available: {e}")

        except Exception as e:
            logger.debug(f"Failed to collect VPN data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="vpn").inc()

    async def _collect_led_metrics(self):
        """Collect LED and Aura metrics"""
        try:
            # LED status
            try:
                led_data = await self.router.async_get_data(AsusData.LED)
                if led_data and "state" in led_data:
                    LED_STATUS.set(1 if led_data["state"] else 0)
                    logger.debug("Collected LED metrics")
            except Exception as e:
                logger.debug(f"LED metrics not available: {e}")

            # Aura lighting
            try:
                aura_data = await self.router.async_get_data(AsusData.AURA)
                if aura_data and "state" in aura_data:
                    AURA_STATUS.set(aura_data["state"])
                    logger.debug("Collected Aura metrics")
            except Exception as e:
                logger.debug(f"Aura metrics not available: {e}")

        except Exception as e:
            logger.debug(f"Failed to collect LED/Aura data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="led").inc()

    async def metrics_collection_loop(self):
        """Main loop for collecting metrics"""
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(
                    self.collection_interval * 2
                )  # Wait longer on error

    async def metrics_handler(self, request):
        """HTTP handler for Prometheus metrics endpoint"""
        try:
            data = generate_latest()
            return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return web.Response(text="Error generating metrics", status=500)

    async def health_handler(self, request):
        """Health check endpoint"""
        status = "healthy" if self.is_connected else "unhealthy"
        info = {
            "status": status,
            "connection": "connected" if self.is_connected else "disconnected",
            "router": self.hostname,
            "collection_interval": self.collection_interval,
        }
        return web.Response(
            text=f"Status: {status}\n"
            + "\n".join([f"{k}: {v}" for k, v in info.items()])
        )

    async def info_handler(self, request):
        """Info endpoint with metrics overview"""
        info_text = """ASUS Router Prometheus Exporter

Available Endpoints:
- /metrics       - Prometheus metrics
- /health        - Health check
- /info          - This information page

Collected Metrics:
- System: CPU usage, load average, memory usage
- Network: WAN/LAN traffic, port status, client counts
- Hardware: Temperature sensors, port link rates
- WiFi: Client counts by band, association stats
- Services: VPN status, LED status, firmware info

Configuration:
- Router: {hostname}
- Collection Interval: {interval}s
- Log Level: {log_level}
""".format(
            hostname=self.hostname,
            interval=self.collection_interval,
            log_level=log_level,
        )
        return web.Response(text=info_text, content_type="text/plain")

    async def start_server(self):
        """Start the HTTP server"""
        app = web.Application()
        app.router.add_get("/metrics", self.metrics_handler)
        app.router.add_get("/health", self.health_handler)
        app.router.add_get("/info", self.info_handler)
        app.router.add_get("/", self.info_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()
        logger.info(f"Prometheus exporter started on port {self.port}")
        logger.info(f"Metrics available at: http://0.0.0.0:{self.port}/metrics")

    async def run(self):
        """Main run method"""
        logger.info("Starting ASUS Router Prometheus Exporter")
        logger.info(f"Target router: {self.hostname}")
        logger.info(f"Collection interval: {self.collection_interval}s")

        # Connect to router
        await self.connect_router()

        # Start HTTP server
        await self.start_server()

        # Start metrics collection in background
        collection_task = asyncio.create_task(self.metrics_collection_loop())

        try:
            # Keep the server running
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            collection_task.cancel()
            try:
                await collection_task
            except asyncio.CancelledError:
                pass


def main():
    """Main entry point"""
    # Configuration from environment variables or defaults
    hostname = os.getenv("ASUS_HOSTNAME", "192.168.1.1")
    username = os.getenv("ASUS_USERNAME", "admin")
    password = os.getenv("ASUS_PASSWORD")
    use_ssl = os.getenv("ASUS_USE_SSL", "false").lower() == "true"
    port = int(os.getenv("EXPORTER_PORT", "8000"))
    collection_interval = int(os.getenv("EXPORTER_COLLECTION_INTERVAL", "15"))

    if not password:
        logger.error("Password is required. Set ASUS_PASSWORD environment variable.")
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
        print("  ASUS_PASSWORD=mypassword python3 asus_exporter.py")
        sys.exit(1)

    exporter = AsusExporter(
        hostname=hostname,
        username=username,
        password=password,
        use_ssl=use_ssl,
        port=port,
        collection_interval=collection_interval,
    )

    try:
        asyncio.run(exporter.run())
    except KeyboardInterrupt:
        logger.info("Exporter stopped by user")
    except Exception as e:
        logger.error(f"Exporter failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
