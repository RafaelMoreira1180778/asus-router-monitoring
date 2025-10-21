"""WiFi and client metrics collector"""

from typing import Any

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    CLIENT_COUNT_BY_TYPE,
    CLIENT_INTERNET_STATE,
    CLIENT_ONLINE,
    CLIENT_RSSI,
    CLIENT_RX_RATE,
    CLIENT_TX_RATE,
    COLLECTION_ERRORS_TOTAL,
    GWLAN_CLIENT_COUNT,
    GWLAN_STATUS,
    WIFI_CLIENTS_ASSOCIATED,
    WIFI_CLIENTS_AUTHENTICATED,
    WIFI_CLIENTS_AUTHORIZED,
    WIFI_CLIENTS_BY_BAND,
    WIFI_CLIENTS_TOTAL,
    WLAN_BANDWIDTH,
    WLAN_CHANNEL,
    WLAN_STATUS,
    WLAN_TXPOWER,
)
from .base import BaseCollector


class WiFiCollector(BaseCollector):
    """Collects WiFi and client connection metrics"""

    def get_data_types(self) -> list[AsusData]:
        return [AsusData.CLIENTS, AsusData.SYSINFO, AsusData.GWLAN, AsusData.WLAN]

    async def collect(self) -> dict[str, Any]:
        """Collect WiFi and client metrics"""
        metrics = {}

        try:
            await self._collect_wifi_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect WiFi client data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="wifi").inc()

        try:
            await self._collect_client_details(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect detailed client data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="client_details").inc()

        try:
            await self._collect_sysinfo_wifi(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect sysinfo WiFi data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="sysinfo_wifi").inc()

        try:
            await self._collect_guest_wlan_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect guest WLAN data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="gwlan").inc()

        try:
            await self._collect_wlan_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect WLAN data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="wlan").inc()

        return metrics

    async def _collect_wifi_metrics(self, metrics: dict[str, Any]):
        """Collect WiFi client metrics"""
        wifi_data = await self.router.async_get_data(AsusData.CLIENTS)
        if wifi_data:
            total_clients = len(wifi_data)
            WIFI_CLIENTS_TOTAL.set(total_clients)
            metrics["wifi_clients_total"] = total_clients

            # Count clients by band if available
            bands = {}
            for client in wifi_data.values():
                if isinstance(client, dict) and "band" in client:
                    band = str(client["band"])
                    bands[band] = bands.get(band, 0) + 1

            for band, count in bands.items():
                WIFI_CLIENTS_BY_BAND.labels(band=band).set(count)
                metrics[f"wifi_clients_band_{band}"] = count

            self.logger.debug(f"WiFi clients: total={total_clients}, by band={bands}")

    async def _collect_client_details(self, metrics: dict[str, Any]):
        """Collect detailed client metrics including individual client data"""
        clients_data = await self.router.async_get_data(AsusData.CLIENTS)
        if clients_data:
            # Count clients by connection type
            connection_counts = {}
            wifi_clients = 0
            wired_clients = 0

            for client_mac, client_info in clients_data.items():
                if isinstance(client_info, dict):
                    mac = str(client_mac)
                    name = client_info.get("name", client_info.get("nickName", "Unknown"))[
                        :50
                    ]  # Limit name length

                    # Determine connection type
                    is_wireless = client_info.get("isWL", "0")
                    # Handle both string and numeric representations
                    is_wireless_str = str(is_wireless)
                    if hasattr(is_wireless, "value"):
                        is_wireless_str = str(is_wireless.value)

                    connection_type = "unknown"

                    if is_wireless_str == "0":
                        connection_type = "wired"
                        wired_clients += 1
                    elif is_wireless_str == "1":
                        connection_type = "wifi_2g"
                        wifi_clients += 1
                    elif is_wireless_str == "2":
                        connection_type = "wifi_5g"
                        wifi_clients += 1
                    elif is_wireless_str == "3":
                        connection_type = "wifi_6g"
                        wifi_clients += 1

                    connection_counts[connection_type] = (
                        connection_counts.get(connection_type, 0) + 1
                    )

                    # Online status
                    is_online = client_info.get("isOnline", "0")
                    CLIENT_ONLINE.labels(mac=mac, name=name, connection_type=connection_type).set(
                        1 if is_online == "1" else 0
                    )

                    # RSSI for wireless clients
                    if is_wireless != "0" and "rssi" in client_info:
                        try:
                            rssi_value = float(client_info["rssi"])
                            band = (
                                "2g" if is_wireless == "1" else "5g" if is_wireless == "2" else "6g"
                            )
                            CLIENT_RSSI.labels(mac=mac, name=name, band=band).set(rssi_value)
                        except (ValueError, TypeError):
                            pass

                    # TX rate
                    if "curTx" in client_info and client_info["curTx"] is not None:
                        try:
                            tx_rate = float(client_info["curTx"])
                            CLIENT_TX_RATE.labels(
                                mac=mac, name=name, connection_type=connection_type
                            ).set(tx_rate)
                        except (ValueError, TypeError):
                            pass

                    # RX rate
                    if "curRx" in client_info and client_info["curRx"] is not None:
                        try:
                            rx_rate = float(client_info["curRx"])
                            CLIENT_RX_RATE.labels(
                                mac=mac, name=name, connection_type=connection_type
                            ).set(rx_rate)
                        except (ValueError, TypeError):
                            pass

                    # Internet access state
                    internet_state = client_info.get("internetState", "0")
                    try:
                        internet_value = int(internet_state)
                        CLIENT_INTERNET_STATE.labels(
                            mac=mac, name=name, connection_type=connection_type
                        ).set(internet_value)
                    except (ValueError, TypeError):
                        pass

            # Set connection type counts
            for conn_type, count in connection_counts.items():
                CLIENT_COUNT_BY_TYPE.labels(type=conn_type).set(count)
                metrics[f"client_count_{conn_type}"] = count

            # Set totals
            CLIENT_COUNT_BY_TYPE.labels(type="wifi_total").set(wifi_clients)
            CLIENT_COUNT_BY_TYPE.labels(type="wired_total").set(wired_clients)
            CLIENT_COUNT_BY_TYPE.labels(type="total").set(len(clients_data))

            metrics["wifi_clients_total_count"] = wifi_clients
            metrics["wired_clients_total_count"] = wired_clients
            metrics["total_clients_count"] = len(clients_data)

            self.logger.debug(f"Collected detailed metrics for {len(clients_data)} clients")

    async def _collect_sysinfo_wifi(self, metrics: dict[str, Any]):
        """Collect WiFi client details from sysinfo"""
        sysinfo_data = await self.router.async_get_data(AsusData.SYSINFO)
        if sysinfo_data:
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
                            metric_gauge.labels(band=band_name).set(float(stats[metric_name]))
                            metrics[f"wifi_{band_name}_{metric_name}"] = stats[metric_name]

    async def _collect_guest_wlan_metrics(self, metrics: dict[str, Any]):
        """Collect Guest WLAN metrics"""
        try:
            gwlan_data = await self.router.async_get_data(AsusData.GWLAN)
            if gwlan_data:
                for band, stats in gwlan_data.items():
                    if isinstance(stats, dict):
                        # Guest WLAN status
                        if "status" in stats:
                            GWLAN_STATUS.labels(band=band, guest_id="1").set(
                                1 if stats["status"] else 0
                            )
                            metrics[f"gwlan_{band}_status"] = stats["status"]

                        # Guest client count
                        if "client_count" in stats:
                            GWLAN_CLIENT_COUNT.labels(band=band, guest_id="1").set(
                                stats["client_count"]
                            )
                            metrics[f"gwlan_{band}_client_count"] = stats["client_count"]

                self.logger.debug("Collected Guest WLAN metrics")
        except Exception as e:
            self.logger.debug(f"Guest WLAN metrics not available: {e}")

    async def _collect_wlan_metrics(self, metrics: dict[str, Any]):
        """Collect WLAN (main WiFi) metrics"""
        try:
            wlan_data = await self.router.async_get_data(AsusData.WLAN)
            if wlan_data:
                for band, stats in wlan_data.items():
                    if isinstance(stats, dict):
                        # WLAN status
                        if "status" in stats:
                            WLAN_STATUS.labels(band=band).set(1 if stats["status"] else 0)
                            metrics[f"wlan_{band}_status"] = stats["status"]

                        # WLAN channel
                        if "channel" in stats:
                            WLAN_CHANNEL.labels(band=band).set(stats["channel"])
                            metrics[f"wlan_{band}_channel"] = stats["channel"]

                        # WLAN transmit power
                        if "txpower" in stats:
                            WLAN_TXPOWER.labels(band=band).set(stats["txpower"])
                            metrics[f"wlan_{band}_txpower"] = stats["txpower"]

                        # WLAN bandwidth
                        if "bandwidth" in stats:
                            WLAN_BANDWIDTH.labels(band=band).set(stats["bandwidth"])
                            metrics[f"wlan_{band}_bandwidth"] = stats["bandwidth"]

                self.logger.debug("Collected WLAN metrics")
        except Exception as e:
            self.logger.debug(f"WLAN metrics not available: {e}")
