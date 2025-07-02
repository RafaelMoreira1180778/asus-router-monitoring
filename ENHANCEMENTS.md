# ASUS Router Exporter Enhancements

## Summary of New Metrics

Based on your existing metrics output and analysis of the AsusRouter library, I've enhanced the exporter with several new categories of metrics that provide much more detailed insights into your network performance and client behavior.

## New Metrics Added

### 1. Client Connection Metrics
- **asus_client_count_by_type{type}** - Count of clients by connection type (wired, wifi_2g, wifi_5g, wifi_6g, totals)
- **asus_client_online{mac, name, connection_type}** - Individual client online status (1=online, 0=offline)
- **asus_client_rssi_dbm{mac, name, band}** - WiFi client signal strength in dBm
- **asus_client_tx_rate_mbps{mac, name, connection_type}** - Individual client upload speed in Mbps
- **asus_client_rx_rate_mbps{mac, name, connection_type}** - Individual client download speed in Mbps
- **asus_client_internet_state{mac, name, connection_type}** - Client internet access permission (1=allowed, 0=blocked)

### 2. Speedtest Metrics
- **asus_speedtest_download_mbps** - Router's measured download speed
- **asus_speedtest_upload_mbps** - Router's measured upload speed  
- **asus_speedtest_ping_ms** - Router's measured ping latency
- **asus_speedtest_timestamp_seconds** - When the last speedtest was performed

### 3. Enhanced Port Metrics
- **asus_port_max_rate_mbps{node_mac, port_type, port_id}** - Maximum capable speed of each port
- **asus_port_capabilities{node_mac, port_type, port_id, capability}** - Port capability flags

### 4. Node Information
- **asus_node_status{node_mac, attribute}** - Additional node status information for mesh networks

## Key Benefits

### Individual Client Monitoring
You can now monitor each connected device individually:
- See real-time upload/download speeds for each client
- Monitor WiFi signal strength (RSSI) for wireless devices
- Track which devices are online/offline
- Identify which devices have internet access blocked

### Network Performance Insights
- Router's own speedtest results show your actual ISP performance
- Enhanced port information shows maximum capabilities vs current usage
- Connection type classification helps identify network bottlenecks

### Troubleshooting Capabilities
- Identify clients with poor WiFi signal strength
- Find bandwidth-heavy users in real-time
- Monitor port utilization and capabilities
- Track internet access permissions per device

## Enhanced Grafana Dashboard

I've created a new enhanced dashboard (`asus-router-enhanced-dashboard.json`) that includes:

1. **Client Type Distribution** - Pie chart showing wired vs WiFi clients
2. **Top Client Bandwidth Usage** - Real-time view of highest bandwidth users
3. **Client Details Table** - Comprehensive table with:
   - Device name and MAC address
   - Connection type (wired/wifi band)
   - Online status with color coding
   - RSSI for WiFi devices with signal strength colors
   - Real-time TX/RX rates
4. **Port Status Table** - Enhanced port information with max rates
5. **Speedtest Results** - Router's own speed test measurements

## Usage Examples

### Find Devices with Poor WiFi Signal
```
asus_client_rssi_dbm < -70
```

### Monitor Top Bandwidth Users
```
topk(10, asus_client_tx_rate_mbps + asus_client_rx_rate_mbps)
```

### Count Active WiFi vs Wired Clients
```
asus_client_count_by_type{type="wifi_total"}
asus_client_count_by_type{type="wired_total"}
```

### Identify Offline Devices
```
asus_client_online == 0
```

## Running the Enhanced Exporter

The enhanced exporter maintains backward compatibility with all existing metrics while adding the new ones. Simply restart your exporter and the new metrics will be available immediately.

The enhanced dashboard provides a much more comprehensive view of your network, showing not just aggregate statistics but individual device performance and behavior.
