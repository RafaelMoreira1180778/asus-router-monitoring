"""VPN metrics collector (OpenVPN, WireGuard, VPNC)"""

from typing import Any

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    COLLECTION_ERRORS_TOTAL,
    OPENVPN_CLIENT_STATUS,
    OPENVPN_SERVER_STATUS,
    VPNC_CLIENT_COUNT,
    VPNC_CLIENT_TRAFFIC_RX,
    VPNC_CLIENT_TRAFFIC_TX,
    VPNC_CLIENT_UPTIME,
    WIREGUARD_CLIENT_STATUS,
    WIREGUARD_SERVER_STATUS,
)
from .base import BaseCollector


class VPNCollector(BaseCollector):
    """Collects VPN-related metrics"""

    def get_data_types(self) -> list[AsusData]:
        return [AsusData.OPENVPN, AsusData.WIREGUARD, AsusData.VPNC]

    async def collect(self) -> dict[str, Any]:
        """Collect VPN metrics"""
        metrics = {}

        try:
            await self._collect_openvpn_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect OpenVPN data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="openvpn").inc()

        try:
            await self._collect_wireguard_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect WireGuard data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="wireguard").inc()

        try:
            await self._collect_vpnc_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect VPNC data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="vpnc").inc()

        return metrics

    async def _collect_openvpn_metrics(self, metrics: dict[str, Any]):
        """Collect OpenVPN metrics"""
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
                        OPENVPN_CLIENT_STATUS.labels(client_id=str(client_id)).set(state_value)
                        metrics[f"openvpn_client_{client_id}_status"] = state_value

                # Server metrics
                servers = openvpn_data.get("server", {})
                for server_id, server_info in servers.items():
                    if isinstance(server_info, dict) and "state" in server_info:
                        state_value = server_info["state"]
                        if hasattr(state_value, "value"):
                            state_value = state_value.value
                        OPENVPN_SERVER_STATUS.labels(server_id=str(server_id)).set(state_value)
                        metrics[f"openvpn_server_{server_id}_status"] = state_value

                self.logger.debug("Collected OpenVPN metrics")
        except Exception as e:
            self.logger.debug(f"OpenVPN metrics not available: {e}")

    async def _collect_wireguard_metrics(self, metrics: dict[str, Any]):
        """Collect WireGuard metrics"""
        try:
            # WireGuard client metrics
            wg_client_data = await self.router.async_get_data(AsusData.WIREGUARD_CLIENT)
            if wg_client_data:
                for client_id, client_info in wg_client_data.items():
                    if isinstance(client_info, dict) and "state" in client_info:
                        state_value = client_info["state"]
                        if hasattr(state_value, "value"):
                            state_value = state_value.value
                        WIREGUARD_CLIENT_STATUS.labels(client_id=str(client_id)).set(state_value)
                        metrics[f"wireguard_client_{client_id}_status"] = state_value

                self.logger.debug("Collected WireGuard client metrics")
        except Exception as e:
            self.logger.debug(f"WireGuard client metrics not available: {e}")

        try:
            # WireGuard server metrics
            wg_server_data = await self.router.async_get_data(AsusData.WIREGUARD_SERVER)
            if wg_server_data:
                for server_id, server_info in wg_server_data.items():
                    if isinstance(server_info, dict) and "state" in server_info:
                        state_value = server_info["state"]
                        if hasattr(state_value, "value"):
                            state_value = state_value.value
                        WIREGUARD_SERVER_STATUS.labels(server_id=str(server_id)).set(state_value)
                        metrics[f"wireguard_server_{server_id}_status"] = state_value

                self.logger.debug("Collected WireGuard server metrics")
        except Exception as e:
            self.logger.debug(f"WireGuard server metrics not available: {e}")

    async def _collect_vpnc_metrics(self, metrics: dict[str, Any]):
        """Collect VPNC (VPN Client) metrics"""
        try:
            vpnc_data = await self.router.async_get_data(AsusData.VPNC)
            if vpnc_data:
                # Client count
                if "client_count" in vpnc_data:
                    VPNC_CLIENT_COUNT.set(vpnc_data["client_count"])
                    metrics["vpnc_client_count"] = vpnc_data["client_count"]

                # Client uptime and traffic
                clients = vpnc_data.get("clients", {})
                for client_id, client_info in clients.items():
                    if isinstance(client_info, dict):
                        # Uptime
                        if "uptime" in client_info:
                            VPNC_CLIENT_UPTIME.labels(client_id=client_id).set(
                                client_info["uptime"]
                            )
                            metrics[f"vpnc_client_{client_id}_uptime"] = client_info["uptime"]

                        # Traffic RX
                        if "traffic_rx" in client_info:
                            VPNC_CLIENT_TRAFFIC_RX.labels(client_id=client_id).inc(
                                client_info["traffic_rx"]
                            )
                            metrics[f"vpnc_client_{client_id}_traffic_rx"] = client_info[
                                "traffic_rx"
                            ]

                        # Traffic TX
                        if "traffic_tx" in client_info:
                            VPNC_CLIENT_TRAFFIC_TX.labels(client_id=client_id).inc(
                                client_info["traffic_tx"]
                            )
                            metrics[f"vpnc_client_{client_id}_traffic_tx"] = client_info[
                                "traffic_tx"
                            ]

                self.logger.debug("Collected VPNC metrics")
        except Exception as e:
            self.logger.debug(f"VPNC metrics not available: {e}")
