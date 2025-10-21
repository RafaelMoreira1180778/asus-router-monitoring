"""Additional services collector (LED, Aura, Speedtest, etc.)"""

from typing import Any

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    AIMESH_NODE_COUNT,
    AIMESH_NODE_STATUS,
    AURA_STATUS,
    COLLECTION_ERRORS_TOTAL,
    DSL_RATE_DOWN,
    DSL_RATE_UP,
    DSL_SNR_DOWN,
    DSL_SNR_UP,
    LED_STATUS,
    PARENTAL_CONTROL_BLOCKED_CLIENTS,
    PARENTAL_CONTROL_ENABLED,
    PARENTAL_CONTROL_RULES,
    PING_PACKET_LOSS,
    PING_RESPONSE_TIME,
    PORT_FORWARDING_ENABLED,
    PORT_FORWARDING_RULES,
    SPEEDTEST_DOWNLOAD_MBPS,
    SPEEDTEST_PING_MS,
    SPEEDTEST_TIMESTAMP,
    SPEEDTEST_UPLOAD_MBPS,
)
from .base import BaseCollector


class ServicesCollector(BaseCollector):
    """Collects additional service metrics"""

    def get_data_types(self) -> list[AsusData]:
        return [
            AsusData.LED,
            AsusData.AURA,
            AsusData.SPEEDTEST,
            AsusData.AIMESH,
            AsusData.DSL,
            AsusData.PARENTAL_CONTROL,
            AsusData.PORT_FORWARDING,
            AsusData.PING,
        ]

    async def collect(self) -> dict[str, Any]:
        """Collect service metrics"""
        metrics = {}

        try:
            await self._collect_led_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect LED data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="led").inc()

        try:
            await self._collect_speedtest_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect speedtest data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="speedtest").inc()

        try:
            await self._collect_aimesh_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect AiMesh data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="aimesh").inc()

        try:
            await self._collect_dsl_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect DSL data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="dsl").inc()

        try:
            await self._collect_parental_control_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect parental control data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="parental_control").inc()

        try:
            await self._collect_port_forwarding_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect port forwarding data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="port_forwarding").inc()

        try:
            await self._collect_ping_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect ping data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="ping").inc()

        return metrics

    async def _collect_led_metrics(self, metrics: dict[str, Any]):
        """Collect LED and Aura metrics"""
        # LED status
        try:
            led_data = await self.router.async_get_data(AsusData.LED)
            if led_data and "state" in led_data:
                led_status = 1 if led_data["state"] else 0
                LED_STATUS.set(led_status)
                metrics["led_status"] = led_status
                self.logger.debug("Collected LED metrics")
        except Exception as e:
            self.logger.debug(f"LED metrics not available: {e}")

        # Aura lighting
        try:
            aura_data = await self.router.async_get_data(AsusData.AURA)
            if aura_data and "state" in aura_data:
                AURA_STATUS.set(aura_data["state"])
                metrics["aura_status"] = aura_data["state"]
                self.logger.debug("Collected Aura metrics")
        except Exception as e:
            self.logger.debug(f"Aura metrics not available: {e}")

    async def _collect_speedtest_metrics(self, metrics: dict[str, Any]):
        """Collect speedtest metrics"""
        try:
            speedtest_data = await self.router.async_get_data(AsusData.SPEEDTEST_RESULT)
            if speedtest_data:
                result = speedtest_data.get("result")
                if result and isinstance(result, dict):
                    # Download speed
                    if "download" in result:
                        try:
                            download_mbps = float(result["download"])
                            SPEEDTEST_DOWNLOAD_MBPS.set(download_mbps)
                            metrics["speedtest_download_mbps"] = download_mbps
                        except (ValueError, TypeError):
                            pass

                    # Upload speed
                    if "upload" in result:
                        try:
                            upload_mbps = float(result["upload"])
                            SPEEDTEST_UPLOAD_MBPS.set(upload_mbps)
                            metrics["speedtest_upload_mbps"] = upload_mbps
                        except (ValueError, TypeError):
                            pass

                    # Ping
                    if "ping" in result:
                        try:
                            ping_ms = float(result["ping"])
                            SPEEDTEST_PING_MS.set(ping_ms)
                            metrics["speedtest_ping_ms"] = ping_ms
                        except (ValueError, TypeError):
                            pass

                    # Timestamp
                    if "timestamp" in result:
                        try:
                            timestamp = float(result["timestamp"])
                            SPEEDTEST_TIMESTAMP.set(timestamp)
                            metrics["speedtest_timestamp"] = timestamp
                        except (ValueError, TypeError):
                            pass

                self.logger.debug("Collected speedtest metrics")
        except Exception as e:
            self.logger.debug(f"Speedtest metrics not available: {e}")

    async def _collect_aimesh_metrics(self, metrics: dict[str, Any]):
        """Collect AiMesh metrics"""
        try:
            aimesh_data = await self.router.async_get_data(AsusData.AIMESH)
            if aimesh_data:
                # Node count
                if "node_count" in aimesh_data:
                    AIMESH_NODE_COUNT.set(aimesh_data["node_count"])
                    metrics["aimesh_node_count"] = aimesh_data["node_count"]

                # Node status
                nodes = aimesh_data.get("nodes", {})
                for node_mac, node_info in nodes.items():
                    if isinstance(node_info, dict) and "status" in node_info:
                        status_value = node_info["status"]
                        if hasattr(status_value, "value"):
                            status_value = status_value.value
                        node_model = node_info.get("model", "unknown")
                        AIMESH_NODE_STATUS.labels(node_mac=node_mac, node_model=node_model).set(
                            status_value
                        )
                        metrics[f"aimesh_node_{node_mac}_status"] = status_value

                self.logger.debug("Collected AiMesh metrics")
        except Exception as e:
            self.logger.debug(f"AiMesh metrics not available: {e}")

    async def _collect_dsl_metrics(self, metrics: dict[str, Any]):
        """Collect DSL metrics"""
        try:
            dsl_data = await self.router.async_get_data(AsusData.DSL)
            if dsl_data:
                # Downstream and upstream rates
                if "rate_down" in dsl_data:
                    DSL_RATE_DOWN.set(float(dsl_data["rate_down"]))
                    metrics["dsl_rate_down"] = dsl_data["rate_down"]
                if "rate_up" in dsl_data:
                    DSL_RATE_UP.set(float(dsl_data["rate_up"]))
                    metrics["dsl_rate_up"] = dsl_data["rate_up"]

                # SNR values
                if "snr_down" in dsl_data:
                    DSL_SNR_DOWN.set(float(dsl_data["snr_down"]))
                    metrics["dsl_snr_down"] = dsl_data["snr_down"]
                if "snr_up" in dsl_data:
                    DSL_SNR_UP.set(float(dsl_data["snr_up"]))
                    metrics["dsl_snr_up"] = dsl_data["snr_up"]

                self.logger.debug("Collected DSL metrics")
        except Exception as e:
            self.logger.debug(f"DSL metrics not available: {e}")

    async def _collect_parental_control_metrics(self, metrics: dict[str, Any]):
        """Collect Parental Control metrics"""
        try:
            parental_data = await self.router.async_get_data(AsusData.PARENTAL_CONTROL)
            if parental_data:
                # Enabled status
                if "enabled" in parental_data:
                    enabled = 1 if parental_data["enabled"] else 0
                    PARENTAL_CONTROL_ENABLED.set(enabled)
                    metrics["parental_control_enabled"] = enabled

                # Rules count
                if "rules" in parental_data:
                    rules_count = len(parental_data["rules"])
                    PARENTAL_CONTROL_RULES.set(rules_count)
                    metrics["parental_control_rules"] = rules_count

                # Blocked clients count
                if "blocked_clients" in parental_data:
                    blocked_count = len(parental_data["blocked_clients"])
                    PARENTAL_CONTROL_BLOCKED_CLIENTS.set(blocked_count)
                    metrics["parental_control_blocked_clients"] = blocked_count

                self.logger.debug("Collected Parental Control metrics")
        except Exception as e:
            self.logger.debug(f"Parental Control metrics not available: {e}")

    async def _collect_port_forwarding_metrics(self, metrics: dict[str, Any]):
        """Collect Port Forwarding metrics"""
        try:
            port_forwarding_data = await self.router.async_get_data(AsusData.PORT_FORWARDING)
            if port_forwarding_data:
                # Enabled status
                if "enabled" in port_forwarding_data:
                    enabled = 1 if port_forwarding_data["enabled"] else 0
                    PORT_FORWARDING_ENABLED.set(enabled)
                    metrics["port_forwarding_enabled"] = enabled

                # Rules count
                if "rules" in port_forwarding_data:
                    rules_count = len(port_forwarding_data["rules"])
                    PORT_FORWARDING_RULES.set(rules_count)
                    metrics["port_forwarding_rules"] = rules_count

                self.logger.debug("Collected Port Forwarding metrics")
        except Exception as e:
            self.logger.debug(f"Port Forwarding metrics not available: {e}")

    async def _collect_ping_metrics(self, metrics: dict[str, Any]):
        """Collect Network Ping metrics"""
        try:
            ping_data = await self.router.async_get_data(AsusData.PING)
            if ping_data:
                for target, stats in ping_data.items():
                    if isinstance(stats, dict):
                        # Response time
                        if "response_time" in stats:
                            PING_RESPONSE_TIME.labels(target=target).set(stats["response_time"])
                            metrics[f"ping_{target}_response_time"] = stats["response_time"]

                        # Packet loss
                        if "packet_loss" in stats:
                            PING_PACKET_LOSS.labels(target=target).set(stats["packet_loss"])
                            metrics[f"ping_{target}_packet_loss"] = stats["packet_loss"]

                self.logger.debug("Collected Network Ping metrics")
        except Exception as e:
            self.logger.debug(f"Network Ping metrics not available: {e}")
