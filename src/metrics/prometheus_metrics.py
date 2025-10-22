"""
Prometheus metrics definitions for ASUS Router Exporter
"""

from prometheus_client import Counter, Gauge, Histogram, Info

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
WAN_STATUS = Gauge("asus_wan_status", "WAN connection status")
WAN_IP_ADDRESS = Info("asus_wan_ip", "WAN IP address information")
WAN_DNS_SERVERS = Info("asus_wan_dns", "WAN DNS servers information")
WAN_UPTIME = Gauge("asus_wan_uptime_seconds", "WAN connection uptime in seconds")

# Network interface metrics - LAN/WiFi
INTERFACE_RX_BYTES = Counter(
    "asus_interface_rx_bytes_total", "Interface RX bytes total", ["interface"]
)
INTERFACE_TX_BYTES = Counter(
    "asus_interface_tx_bytes_total", "Interface TX bytes total", ["interface"]
)

# Port metrics
PORT_STATUS = Gauge("asus_port_status", "Port status (1=up, 0=down)", ["port_type", "port_id"])
PORT_LINK_RATE = Gauge(
    "asus_port_link_rate_mbps", "Port link rate in Mbps", ["port_type", "port_id"]
)
PORT_MAX_RATE = Gauge(
    "asus_port_max_rate_mbps",
    "Port maximum rate in Mbps",
    ["node_mac", "port_type", "port_id"],
)
PORT_CAPABILITIES = Gauge(
    "asus_port_capabilities",
    "Port capabilities",
    ["node_mac", "port_type", "port_id", "capability"],
)

# Temperature metrics
TEMPERATURE = Gauge("asus_temperature_celsius", "Temperature in Celsius", ["sensor"])

# WiFi client metrics
WIFI_CLIENTS_TOTAL = Gauge("asus_wifi_clients_total", "Total number of WiFi clients")
WIFI_CLIENTS_BY_BAND = Gauge(
    "asus_wifi_clients_by_band", "Number of WiFi clients by band", ["band"]
)
WIFI_CLIENTS_ASSOCIATED = Gauge("asus_wifi_clients_associated", "WiFi clients associated", ["band"])
WIFI_CLIENTS_AUTHORIZED = Gauge("asus_wifi_clients_authorized", "WiFi clients authorized", ["band"])
WIFI_CLIENTS_AUTHENTICATED = Gauge(
    "asus_wifi_clients_authenticated", "WiFi clients authenticated", ["band"]
)

# Client connection metrics
CLIENT_COUNT_BY_TYPE = Gauge(
    "asus_client_count_by_type", "Number of clients by connection type", ["type"]
)
CLIENT_ONLINE = Gauge(
    "asus_client_online", "Client online status", ["mac", "name", "connection_type"]
)
CLIENT_RSSI = Gauge("asus_client_rssi_dbm", "Client RSSI in dBm", ["mac", "name", "band"])
CLIENT_TX_RATE = Gauge(
    "asus_client_tx_rate_mbps",
    "Client TX rate in Mbps",
    ["mac", "name", "connection_type"],
)
CLIENT_RX_RATE = Gauge(
    "asus_client_rx_rate_mbps",
    "Client RX rate in Mbps",
    ["mac", "name", "connection_type"],
)
CLIENT_INTERNET_STATE = Gauge(
    "asus_client_internet_state",
    "Client internet access state",
    ["mac", "name", "connection_type"],
)

# Connection metrics
CONNECTION_STATUS = Gauge(
    "asus_connection_status", "Router connection status (1=connected, 0=disconnected)"
)
TOTAL_CONNECTIONS = Gauge("asus_connections_total", "Total network connections")
ACTIVE_CONNECTIONS = Gauge("asus_connections_active", "Active network connections")

# Device inventory metrics
DEVICE_INFO = Info("asus_device", "Device information", ["mac", "name", "ip"])
DEVICE_ONLINE = Gauge(
    "asus_device_online",
    "Device online status",
    ["mac", "name", "ip", "connection_type"],
)
DEVICE_CONNECTION_INFO = Info(
    "asus_device_connection", "Device connection details", ["mac", "name", "ip"]
)

# System info
ROUTER_INFO = Info("asus_router", "Router information")
BOOTTIME = Gauge("asus_boot_timestamp_seconds", "Router boot timestamp")

# Firmware info
FIRMWARE_INFO = Info("asus_firmware", "Firmware information")
FIRMWARE_UPDATE_AVAILABLE = Gauge(
    "asus_firmware_update_available", "Firmware update available (1=yes, 0=no)"
)
FIRMWARE_BUILD_INFO = Info("asus_firmware_build", "Firmware build information")
FIRMWARE_RELEASE_NOTES = Info("asus_firmware_notes", "Firmware release notes")

# VPN metrics
OPENVPN_CLIENT_STATUS = Gauge("asus_openvpn_client_status", "OpenVPN client status", ["client_id"])
OPENVPN_SERVER_STATUS = Gauge("asus_openvpn_server_status", "OpenVPN server status", ["server_id"])
WIREGUARD_CLIENT_STATUS = Gauge(
    "asus_wireguard_client_status", "WireGuard client status", ["client_id"]
)
WIREGUARD_SERVER_STATUS = Gauge(
    "asus_wireguard_server_status", "WireGuard server status", ["server_id"]
)

# VPNC (VPN Client) additional metrics
VPNC_CLIENT_COUNT = Gauge("asus_vpnc_client_count", "Number of configured VPN clients")
VPNC_CLIENT_UPTIME = Gauge(
    "asus_vpnc_client_uptime_seconds", "VPN client uptime in seconds", ["client_id"]
)
VPNC_CLIENT_TRAFFIC_RX = Counter(
    "asus_vpnc_client_rx_bytes_total", "VPN client RX bytes total", ["client_id"]
)
VPNC_CLIENT_TRAFFIC_TX = Counter(
    "asus_vpnc_client_tx_bytes_total", "VPN client TX bytes total", ["client_id"]
)

# LED and Aura metrics
LED_STATUS = Gauge("asus_led_status", "LED status (1=on, 0=off)")
AURA_STATUS = Gauge("asus_aura_status", "Aura lighting status")

# Speedtest metrics
SPEEDTEST_DOWNLOAD_MBPS = Gauge("asus_speedtest_download_mbps", "Speedtest download speed in Mbps")
SPEEDTEST_UPLOAD_MBPS = Gauge("asus_speedtest_upload_mbps", "Speedtest upload speed in Mbps")
SPEEDTEST_PING_MS = Gauge("asus_speedtest_ping_ms", "Speedtest ping in milliseconds")
SPEEDTEST_TIMESTAMP = Gauge("asus_speedtest_timestamp_seconds", "Speedtest last run timestamp")

# Node information
NODE_STATUS = Gauge("asus_node_status", "Node status information", ["node_mac", "attribute"])

# AiMesh metrics
AIMESH_NODE_COUNT = Gauge("asus_aimesh_node_count", "Number of AiMesh nodes")
AIMESH_NODE_STATUS = Gauge(
    "asus_aimesh_node_status", "AiMesh node status", ["node_mac", "node_model"]
)

# DSL metrics (for DSL modems)
DSL_RATE_DOWN = Gauge("asus_dsl_rate_down_kbps", "DSL download rate in kbps")
DSL_RATE_UP = Gauge("asus_dsl_rate_up_kbps", "DSL upload rate in kbps")
DSL_SNR_DOWN = Gauge("asus_dsl_snr_down_db", "DSL downstream SNR in dB")
DSL_SNR_UP = Gauge("asus_dsl_snr_up_db", "DSL upstream SNR in dB")

# Guest WLAN metrics
GWLAN_STATUS = Gauge("asus_gwlan_status", "Guest WLAN status", ["band", "guest_id"])
GWLAN_CLIENT_COUNT = Gauge(
    "asus_gwlan_client_count", "Guest WLAN client count", ["band", "guest_id"]
)

# WLAN (main WiFi) metrics
WLAN_STATUS = Gauge("asus_wlan_status", "WLAN status", ["band"])
WLAN_CHANNEL = Gauge("asus_wlan_channel", "WLAN channel", ["band"])
WLAN_TXPOWER = Gauge("asus_wlan_txpower_dbm", "WLAN transmit power in dBm", ["band"])
WLAN_BANDWIDTH = Gauge("asus_wlan_bandwidth_mhz", "WLAN bandwidth in MHz", ["band"])

# Parental Control metrics
PARENTAL_CONTROL_ENABLED = Gauge("asus_parental_control_enabled", "Parental control enabled")
PARENTAL_CONTROL_RULES = Gauge(
    "asus_parental_control_rules_count", "Number of parental control rules"
)
PARENTAL_CONTROL_BLOCKED_CLIENTS = Gauge(
    "asus_parental_control_blocked_clients", "Number of blocked clients"
)

# Port Forwarding metrics
PORT_FORWARDING_ENABLED = Gauge("asus_port_forwarding_enabled", "Port forwarding enabled")
PORT_FORWARDING_RULES = Gauge("asus_port_forwarding_rules_count", "Number of port forwarding rules")

# Network Ping metrics
PING_RESPONSE_TIME = Gauge(
    "asus_ping_response_time_ms", "Ping response time in milliseconds", ["target"]
)
PING_PACKET_LOSS = Gauge("asus_ping_packet_loss_percent", "Ping packet loss percentage", ["target"])

# System flags and capabilities
SYSTEM_FLAGS = Info("asus_system_flags", "System flags and capabilities")

# Device map information
DEVICE_MAP_INFO = Info("asus_device_map", "Device map information")

# Enhanced system information
SYSTEM_MODEL_INFO = Info("asus_system_model", "System model information")
SYSTEM_SERIAL_INFO = Info("asus_system_serial", "System serial information")

# Collection metrics
LAST_COLLECTION_TIMESTAMP = Gauge(
    "asus_last_collection_timestamp_seconds", "Timestamp of last successful collection"
)
COLLECTION_ERRORS_TOTAL = Counter(
    "asus_collection_errors_total", "Total collection errors", ["error_type"]
)
