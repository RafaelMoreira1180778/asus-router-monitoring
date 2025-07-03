"""Hardware metrics collector (Ports, Temperature, etc.)"""

from typing import Any, Dict

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    COLLECTION_ERRORS_TOTAL,
    NODE_STATUS,
    PORT_CAPABILITIES,
    PORT_LINK_RATE,
    PORT_MAX_RATE,
    PORT_STATUS,
    TEMPERATURE,
)
from .base import BaseCollector


class HardwareCollector(BaseCollector):
    """Collects hardware-related metrics"""

    def get_data_types(self) -> list[AsusData]:
        return [AsusData.PORTS, AsusData.TEMPERATURE, AsusData.NODE_INFO]

    async def collect(self) -> Dict[str, Any]:
        """Collect hardware metrics"""
        metrics = {}

        try:
            await self._collect_port_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect port data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="ports").inc()

        try:
            await self._collect_temperature_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect temperature data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="temperature").inc()

        try:
            await self._collect_node_info_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect node info data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="node_info").inc()

        return metrics

    async def _collect_port_metrics(self, metrics: Dict[str, Any]):
        """Collect port status metrics"""
        ports_data = await self.router.async_get_data(AsusData.PORTS)
        if ports_data:
            for node_or_type, ports_info in ports_data.items():
                if isinstance(ports_info, dict):
                    # Handle both formats: node-based and direct port type
                    if all(
                        isinstance(v, dict)
                        and any(isinstance(vv, dict) for vv in v.values())
                        for v in ports_info.values()
                    ):
                        # Node-based format
                        node_mac = str(node_or_type)
                        for port_type, ports in ports_info.items():
                            if isinstance(ports, dict):
                                await self._process_port_data(
                                    ports, str(port_type), node_mac, metrics
                                )
                    else:
                        # Direct port type format
                        await self._process_port_data(
                            ports_info, str(node_or_type), "main", metrics
                        )

            self.logger.debug("Collected port metrics")

    async def _process_port_data(
        self,
        ports: Dict[str, Any],
        port_type_name: str,
        node_mac: str,
        metrics: Dict[str, Any],
    ):
        """Process port data for a specific type and node"""
        for port_id, port_info in ports.items():
            if isinstance(port_info, dict):
                port_id_str = str(port_id)
                metric_key = f"port_{node_mac}_{port_type_name}_{port_id_str}"

                # Port status
                if "state" in port_info:
                    state_value = 1 if port_info["state"] else 0
                    PORT_STATUS.labels(
                        port_type=port_type_name, port_id=port_id_str
                    ).set(state_value)
                    metrics[f"{metric_key}_status"] = state_value

                # Link rate
                if "link_rate" in port_info:
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
                    metrics[f"{metric_key}_link_rate"] = link_rate

                # Maximum rate (enhanced metric)
                if "max_rate" in port_info:
                    max_rate = port_info["max_rate"]
                    if hasattr(max_rate, "value"):
                        max_rate = max_rate.value
                    elif isinstance(max_rate, str):
                        rate_map = {
                            "LINK_10": 10,
                            "LINK_100": 100,
                            "LINK_1000": 1000,
                            "LINK_2500": 2500,
                            "LINK_5000": 5000,
                            "LINK_10000": 10000,
                            "LINK_DOWN": 0,
                        }
                        max_rate = rate_map.get(max_rate, 0)

                    PORT_MAX_RATE.labels(
                        node_mac=node_mac, port_type=port_type_name, port_id=port_id_str
                    ).set(float(max_rate))
                    metrics[f"{metric_key}_max_rate"] = max_rate

                # Port capabilities (enhanced metric)
                if "capabilities" in port_info and isinstance(
                    port_info["capabilities"], list
                ):
                    for capability in port_info["capabilities"]:
                        capability_name = str(capability)
                        if hasattr(capability, "name"):
                            capability_name = capability.name
                        PORT_CAPABILITIES.labels(
                            node_mac=node_mac,
                            port_type=port_type_name,
                            port_id=port_id_str,
                            capability=capability_name,
                        ).set(1)
                        metrics[f"{metric_key}_capability_{capability_name}"] = 1

    async def _collect_temperature_metrics(self, metrics: Dict[str, Any]):
        """Collect temperature metrics"""
        temp_data = await self.router.async_get_data(AsusData.TEMPERATURE)
        if temp_data:
            for sensor, temp in temp_data.items():
                if isinstance(temp, (int, float)):
                    sensor_name = str(sensor)
                    TEMPERATURE.labels(sensor=sensor_name).set(float(temp))
                    metrics[f"temperature_{sensor_name}"] = temp

            self.logger.debug(f"Temperature data: {temp_data}")

    async def _collect_node_info_metrics(self, metrics: Dict[str, Any]):
        """Collect node information metrics"""
        node_data = await self.router.async_get_data(AsusData.NODE_INFO)
        if node_data:
            for node_mac, node_info in node_data.items():
                if isinstance(node_info, dict):
                    for attribute, value in node_info.items():
                        try:
                            numeric_value = float(value) if value is not None else 0
                            NODE_STATUS.labels(
                                node_mac=str(node_mac), attribute=str(attribute)
                            ).set(numeric_value)
                            metrics[f"node_{node_mac}_{attribute}"] = numeric_value
                        except (ValueError, TypeError):
                            # Skip non-numeric values
                            pass

            self.logger.debug("Collected node info metrics")
