"""Device inventory collector for internal network devices"""

from typing import Any

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    COLLECTION_ERRORS_TOTAL,
    DEVICE_CONNECTION_INFO,
    DEVICE_INFO,
    DEVICE_ONLINE,
)
from .base import BaseCollector


class DeviceInventoryCollector(BaseCollector):
    """Collects device inventory information for all connected devices"""

    def get_data_types(self) -> list[AsusData]:
        return [AsusData.CLIENTS]

    async def collect(self) -> dict[str, Any]:
        """Collect device inventory data"""
        metrics = {}

        try:
            await self._collect_device_inventory(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect device inventory: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="device_inventory").inc()

        return metrics

    async def _collect_device_inventory(self, metrics: dict[str, Any]):
        """Collect and process device inventory information"""
        clients_data = await self.router.async_get_data(AsusData.CLIENTS)

        if not clients_data:
            self.logger.debug("No client data available for device inventory")
            return

        self.logger.info(f"Processing device inventory for {len(clients_data)} clients")

        # Log first client to understand data structure
        first_client_logged = True
        if clients_data:
            first_mac = list(clients_data.keys())[0]
            first_client = clients_data[first_mac]
            self.logger.info(
                f"First client type: {type(first_client)}, has_description: {hasattr(first_client, 'description')}, has_connection: {hasattr(first_client, 'connection')}, is_dict: {isinstance(first_client, dict)}"
            )

        device_count = 0
        online_count = 0

        for client_mac, client_info in clients_data.items():
            self.logger.debug(f"Processing client {client_mac}, type: {type(client_info)}")

            # Handle both dict and AsusClient object
            if isinstance(client_info, dict):
                # Raw dict format
                mac = str(client_mac)
                name = client_info.get("name", client_info.get("nickName", "Unknown"))[:50]
                ip_address = client_info.get("ip", "0.0.0.0")
                vendor = client_info.get("vendor", "Unknown")
                is_wireless = client_info.get("isWL", "0")
                is_online = client_info.get("isOnline", "0")
                ip_method = client_info.get("ipMethod", "Unknown")
                internet_mode = client_info.get("internetMode", "Unknown")
                rssi = client_info.get("rssi")
                tx_rate = client_info.get("curTx")
                rx_rate = client_info.get("curRx")
            elif hasattr(client_info, "description") and hasattr(client_info, "connection"):
                # AsusClient object (transformed format from asusrouter v1.21.0+)
                mac = str(client_mac)
                description = client_info.description
                connection = client_info.connection

                name = (description.name if description and description.name else "Unknown")[:50]
                vendor = (description.vendor if description and description.vendor else "Unknown")[
                    :50
                ]
                ip_address = (
                    connection.ip_address if connection and connection.ip_address else "0.0.0.0"
                )

                # Connection type from AsusClient
                conn_type = connection.type if connection else None
                # Map ConnectionType enum to isWL value
                if conn_type:
                    conn_type_str = str(conn_type).lower()
                    if "wired" in conn_type_str or "disconnected" in conn_type_str:
                        is_wireless = "0"
                    elif "2g" in conn_type_str or "2.4" in conn_type_str:
                        is_wireless = "1"
                    elif "5g" in conn_type_str or "5_" in conn_type_str:
                        is_wireless = "2"
                    elif "6g" in conn_type_str:
                        is_wireless = "3"
                    else:
                        is_wireless = "0"  # Default to wired
                else:
                    is_wireless = "0"
                is_online = connection.online if connection else False
                ip_method = connection.ip_method if connection else "Unknown"
                internet_mode = (
                    str(connection.internet_mode)
                    if connection and connection.internet_mode
                    else "Unknown"
                )

                # Wireless specific data
                if hasattr(connection, "rssi"):
                    rssi = connection.rssi
                    tx_rate = connection.tx_speed if hasattr(connection, "tx_speed") else None
                    rx_rate = connection.rx_speed if hasattr(connection, "rx_speed") else None
                else:
                    rssi = None
                    tx_rate = None
                    rx_rate = None
            else:
                self.logger.warning(f"Client {client_mac} is unknown format: {type(client_info)}")
                continue

            try:
                # Log extracted values for first client
                if first_client_logged:
                    self.logger.info(
                        f"Extracted values - MAC: {mac}, Name: {name}, IP: {ip_address}, isWL: {is_wireless}, isOnline: {is_online}"
                    )
                    first_client_logged = False

                # Determine connection type from the is_wireless value we extracted
                connection_type = self._get_connection_type_from_iswl(is_wireless)

                # Normalize online status from the is_online value we extracted
                online_status = self._normalize_online_status(is_online)

                self.logger.debug(
                    f"Device: {name} ({mac}) - IP: {ip_address} - Type: {connection_type} - Online: {online_status}"
                )

                # Set device info metric (static device information)
                DEVICE_INFO.labels(mac=mac, name=name, ip=ip_address).info(
                    {
                        "vendor": str(vendor)[:50],
                        "connection_type": connection_type,
                    }
                )

                # Set online status metric
                DEVICE_ONLINE.labels(
                    mac=mac, name=name, ip=ip_address, connection_type=connection_type
                ).set(1 if online_status else 0)

                # Set detailed connection info
                conn_info_dict = {
                    "connection_type": connection_type,
                    "ip_method": str(ip_method),
                    "internet_mode": str(internet_mode),
                }

                # Add wireless-specific info if applicable
                if connection_type.startswith("wifi_"):
                    if rssi is not None:
                        conn_info_dict["rssi"] = str(rssi)
                    if tx_rate is not None:
                        conn_info_dict["tx_rate_mbps"] = str(tx_rate)
                    if rx_rate is not None:
                        conn_info_dict["rx_rate_mbps"] = str(rx_rate)

                DEVICE_CONNECTION_INFO.labels(mac=mac, name=name, ip=ip_address).info(
                    conn_info_dict
                )

                device_count += 1
                if online_status:
                    online_count += 1

            except Exception as e:
                self.logger.error(f"Error processing device {client_mac}: {e}", exc_info=True)
                continue

        metrics["total_devices"] = device_count
        metrics["online_devices"] = online_count

        self.logger.debug(f"Device inventory: {device_count} total devices, {online_count} online")

    def _get_connection_type_from_iswl(self, is_wireless: Any) -> str:
        """Determine connection type from isWL value"""
        # Handle both string and numeric representations
        is_wireless_str = str(is_wireless)
        if hasattr(is_wireless, "value"):
            is_wireless_str = str(is_wireless.value)

        connection_map = {
            "0": "wired",
            "1": "wifi_2.4ghz",
            "2": "wifi_5ghz",
            "3": "wifi_6ghz",
        }

        return connection_map.get(is_wireless_str, "unknown")

    def _normalize_online_status(self, is_online: Any) -> bool:
        """Normalize online status from various formats"""
        # Handle different representations
        if isinstance(is_online, bool):
            return is_online
        if isinstance(is_online, str):
            return is_online == "1" or is_online.lower() == "true"
        if isinstance(is_online, int):
            return is_online == 1

        # Default to False if we can't determine
        return False
