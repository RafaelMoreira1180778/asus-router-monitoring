"""Hardware metrics collector (Ports, Temperature, etc.)"""

from typing import Any

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

    def _normalize_port_id(self, port_id: Any, port_type: str) -> str:
        """Normalize port ID to a safe string format.

        Handles enums, integers, and other types that might come from asusrouter.
        """
        # If it's an enum, try to get the name first
        if hasattr(port_id, "name"):
            return str(port_id.name).lower()

        # If it has a value attribute (Enum), use that
        port_value = port_id.value if hasattr(port_id, "value") else port_id

        # Convert to string and remove any special characters
        port_str = str(port_value)

        # Map common port type patterns
        if port_type.lower() == "lan":
            # For LAN ports, try to extract just the number
            if isinstance(port_value, int):
                return str(port_value)
            # Remove non-alphanumeric except underscore and dash
            return "".join(c for c in port_str if c.isalnum() or c in "_-").lower()
        elif port_type.lower() == "wan":
            return "wan"
        elif port_type.lower() == "usb":
            return "usb"
        else:
            # Generic cleanup
            return "".join(c for c in port_str if c.isalnum() or c in "_-").lower()

    async def collect(self) -> dict[str, Any]:
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

    async def _collect_port_metrics(self, metrics: dict[str, Any]):
        """Collect port status metrics"""
        ports_data = await self.router.async_get_data(AsusData.PORTS)
        if ports_data:
            self.logger.debug(f"Raw ports_data structure: {ports_data}")
            for node_or_type, ports_info in ports_data.items():
                if isinstance(ports_info, dict):
                    # Handle both formats: node-based and direct port type
                    if all(
                        isinstance(v, dict) and any(isinstance(vv, dict) for vv in v.values())
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
        ports: dict[str, Any],
        port_type_name: str,
        node_mac: str,
        metrics: dict[str, Any],
    ):
        """Process port data for a specific type and node"""
        for port_id, port_info in ports.items():
            if isinstance(port_info, dict):
                # Convert port_id properly - handle enums and integers
                port_id_str = self._normalize_port_id(port_id, port_type_name)
                self.logger.debug(
                    f"Port processing: port_id={port_id} (type={type(port_id).__name__}), port_type={port_type_name}, normalized={port_id_str}, port_info={port_info}"
                )
                metric_key = f"port_{node_mac}_{port_type_name}_{port_id_str}"

                # Port status
                if "state" in port_info:
                    state_value = 1 if port_info["state"] else 0
                    PORT_STATUS.labels(port_type=port_type_name, port_id=port_id_str).set(
                        state_value
                    )
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

                    PORT_LINK_RATE.labels(port_type=port_type_name, port_id=port_id_str).set(
                        float(link_rate)
                    )
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
                if "capabilities" in port_info and isinstance(port_info["capabilities"], list):
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

    async def _collect_temperature_metrics(self, metrics: dict[str, Any]):
        """Collect temperature metrics"""
        temp_data = await self.router.async_get_data(AsusData.TEMPERATURE)
        if temp_data:
            for sensor, temp in temp_data.items():
                if isinstance(temp, (int, float)):
                    sensor_name = str(sensor)
                    TEMPERATURE.labels(sensor=sensor_name).set(float(temp))
                    metrics[f"temperature_{sensor_name}"] = temp

            self.logger.debug(f"Temperature data: {temp_data}")

    async def _collect_node_info_metrics(self, metrics: dict[str, Any]):
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
