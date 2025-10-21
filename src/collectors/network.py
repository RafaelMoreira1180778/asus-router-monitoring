"""Network metrics collector (WAN, LAN, Interfaces, AiMesh)"""

from typing import Any

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    COLLECTION_ERRORS_TOTAL,
    INTERFACE_RX_BYTES,
    INTERFACE_TX_BYTES,
    WAN_DNS_SERVERS,
    WAN_IP_ADDRESS,
    WAN_RX_BYTES,
    WAN_RX_RATE,
    WAN_STATUS,
    WAN_TX_BYTES,
    WAN_TX_RATE,
    WAN_UPTIME,
)
from .base import BaseCollector


class NetworkCollector(BaseCollector):
    """Collects network interface, WAN, and AiMesh traffic metrics (v1.21.0+)"""

    def get_data_types(self) -> list[AsusData]:
        # Include AIMESH_NODE_INFO if available for traffic monitoring (v1.21.0+)
        return [AsusData.WAN, AsusData.NETWORK, AsusData.AIMESH]

    async def collect(self) -> dict[str, Any]:
        """Collect network metrics"""
        metrics = {}

        try:
            await self._collect_wan_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect WAN data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="wan").inc()

        try:
            await self._collect_network_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect network data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="network").inc()

        try:
            await self._collect_aimesh_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect AiMesh data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="aimesh_traffic").inc()

        return metrics

    async def _collect_aimesh_metrics(self, metrics: dict[str, Any]):
        """Collect AiMesh network traffic metrics (v1.21.0+)"""
        try:
            # Try to get AiMesh data for mesh network topology
            aimesh_data = await self.router.async_get_data(AsusData.AIMESH)
            if aimesh_data:
                # AiMesh data structure contains node information
                # Future enhancement: Process mesh network traffic if available
                self.logger.debug("AiMesh network data available for mesh monitoring")
                metrics["aimesh_available"] = True
        except Exception as e:
            self.logger.debug(f"AiMesh traffic monitoring not available: {e}")
            metrics["aimesh_available"] = False

        return metrics

    async def _collect_wan_metrics(self, metrics: dict[str, Any]):
        """Collect WAN metrics"""
        wan_data = await self.router.async_get_data(AsusData.WAN)
        if wan_data:
            if "rx_bytes" in wan_data:
                # Set counter to current value (not increment)
                WAN_RX_BYTES._value.set(float(wan_data["rx_bytes"]))
                metrics["wan_rx_bytes"] = wan_data["rx_bytes"]
            if "tx_bytes" in wan_data:
                # Set counter to current value (not increment)
                WAN_TX_BYTES._value.set(float(wan_data["tx_bytes"]))
                metrics["wan_tx_bytes"] = wan_data["tx_bytes"]
            if "rx_rate" in wan_data:
                WAN_RX_RATE.set(float(wan_data["rx_rate"]))
                metrics["wan_rx_rate"] = wan_data["rx_rate"]
            if "tx_rate" in wan_data:
                WAN_TX_RATE.set(float(wan_data["tx_rate"]))
                metrics["wan_tx_rate"] = wan_data["tx_rate"]

            # WAN status
            if "status" in wan_data:
                status_value = wan_data["status"]
                # Handle different status representations
                if isinstance(status_value, bool):
                    wan_status = 1 if status_value else 0
                elif isinstance(status_value, str):
                    wan_status = (
                        1 if status_value.lower() in ("connected", "up", "true", "1") else 0
                    )
                elif isinstance(status_value, (int, float)):
                    wan_status = 1 if status_value else 0
                elif hasattr(status_value, "value"):
                    # Handle enums
                    wan_status = 1 if status_value.value else 0
                else:
                    wan_status = 1 if status_value else 0

                WAN_STATUS.set(wan_status)
                metrics["wan_status"] = wan_status
                self.logger.debug(
                    f"WAN status: {wan_status} (raw value: {status_value}, type: {type(status_value)})"
                )

            # IP address (Info metric)
            if "ip_address" in wan_data:
                WAN_IP_ADDRESS.info({"address": str(wan_data["ip_address"])})

            # DNS servers (Info metric)
            if "dns_servers" in wan_data:
                dns_servers = wan_data["dns_servers"]
                if isinstance(dns_servers, list):
                    for idx, dns in enumerate(dns_servers):
                        WAN_DNS_SERVERS.labels(index=idx).info({"server": str(dns)})

            # Uptime
            if "uptime" in wan_data:
                WAN_UPTIME.set(float(wan_data["uptime"]))
                metrics["wan_uptime"] = wan_data["uptime"]

            self.logger.debug(
                f"WAN - RX: {wan_data.get('rx_bytes', 'N/A')}, TX: {wan_data.get('tx_bytes', 'N/A')}"
            )

    async def _collect_network_metrics(self, metrics: dict[str, Any]):
        """Collect network interface metrics"""
        network_data = await self.router.async_get_data(AsusData.NETWORK)
        if network_data:
            for interface, stats in network_data.items():
                if isinstance(stats, dict) and "rx" in stats and "tx" in stats:
                    interface_name = str(interface)
                    # Set counter to current value (not increment)
                    INTERFACE_RX_BYTES.labels(interface=interface_name)._value.set(
                        float(stats["rx"])
                    )
                    INTERFACE_TX_BYTES.labels(interface=interface_name)._value.set(
                        float(stats["tx"])
                    )

                    metrics[f"interface_{interface_name}_rx"] = stats["rx"]
                    metrics[f"interface_{interface_name}_tx"] = stats["tx"]

            self.logger.debug("Collected network interface metrics")
