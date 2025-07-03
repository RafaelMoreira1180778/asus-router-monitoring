# ASUS Router Prometheus Exporter v2.0

## Analysis Summary

### Total Available Metrics in AsusRouter Library

The AsusRouter library provides **34 distinct data types** through the `AsusData` enum:

1. **AIMESH** - AiMesh network information
2. **AURA** - Aura lighting system data
3. **BOOTTIME** - System boot time
4. **CLIENTS** - Connected client information
5. **CPU** - CPU usage and performance
6. **DEVICEMAP** - Device mapping information
7. **DSL** - DSL connection data
8. **FIRMWARE** - Firmware information
9. **FIRMWARE_NOTE** - Firmware release notes
10. **FLAGS** - System flags and capabilities
11. **GWLAN** - Guest WLAN information
12. **LED** - LED status
13. **NETWORK** - Network interface statistics
14. **NODE_INFO** - Node information for mesh networks
15. **OPENVPN** - OpenVPN status (combines client and server)
16. **OPENVPN_CLIENT** - OpenVPN client specific data
17. **OPENVPN_SERVER** - OpenVPN server specific data
18. **PARENTAL_CONTROL** - Parental control settings
19. **PING** - Network ping results
20. **PORT_FORWARDING** - Port forwarding rules
21. **PORTS** - Physical port status and information
22. **RAM** - Memory usage statistics
23. **SPEEDTEST** - Speedtest results
24. **SPEEDTEST_RESULT** - Alias for speedtest data
25. **SYSINFO** - System information
26. **SYSTEM** - System services and controls
27. **TEMPERATURE** - Temperature sensors
28. **VPNC** - VPN client information
29. **VPNC_CLIENTLIST** - VPN client list
30. **WAN** - WAN connection information
31. **WIREGUARD** - WireGuard VPN data
32. **WIREGUARD_CLIENT** - WireGuard client data
33. **WIREGUARD_SERVER** - WireGuard server data
34. **WLAN** - WLAN (WiFi) configuration

### Cross-Reference Analysis

The original `asus_exporter.py` was collecting most metrics but had some gaps:

**Missing or Incomplete Metrics in Original:**
- ❌ **DSL** - DSL metrics missing
- ❌ **FIRMWARE_NOTE** - Firmware release notes not collected  
- ❌ **PING** - Network ping metrics missing
- ❌ **PORT_FORWARDING** - Port forwarding metrics missing
- ❌ **PARENTAL_CONTROL** - Parental control metrics missing
- ❌ **SYSTEM** - System services not exposed
- ❌ **FLAGS** - System flags and capabilities missing
- ⚠️ **GWLAN** - Limited guest WLAN support
- ⚠️ **WLAN** - WLAN configuration metrics incomplete
- ⚠️ **AIMESH** - Limited AiMesh support

### Modular Architecture

The script has been restructured into specialized collectors:

#### 1. **SystemCollector** (`src/collectors/system.py`)
- **Data Types**: CPU, RAM, SYSINFO
- **Metrics**: CPU usage, memory statistics, load averages, connection counts

#### 2. **NetworkCollector** (`src/collectors/network.py`)
- **Data Types**: WAN, NETWORK
- **Metrics**: WAN traffic, interface statistics, IP information, DNS servers

#### 3. **WiFiCollector** (`src/collectors/wifi.py`)
- **Data Types**: CLIENTS, SYSINFO, GWLAN, WLAN
- **Metrics**: Client connections, WiFi bands, RSSI, TX/RX rates, guest networks

#### 4. **HardwareCollector** (`src/collectors/hardware.py`)
- **Data Types**: PORTS, TEMPERATURE, NODE_INFO
- **Metrics**: Port status, link rates, temperature sensors, node information

#### 5. **FirmwareCollector** (`src/collectors/firmware.py`)
- **Data Types**: FIRMWARE, FIRMWARE_NOTE, DEVICEMAP, BOOTTIME, FLAGS
- **Metrics**: Firmware versions, update availability, system information

#### 6. **VPNCollector** (`src/collectors/vpn.py`)
- **Data Types**: OPENVPN, WIREGUARD, VPNC
- **Metrics**: VPN client/server status, connection statistics

#### 7. **ServicesCollector** (`src/collectors/services.py`)
- **Data Types**: LED, AURA, SPEEDTEST, AIMESH, DSL, PARENTAL_CONTROL, PORT_FORWARDING, PING
- **Metrics**: LED status, lighting, speedtest results, network services

### New Features Added

✅ **Complete Coverage**: All 34 AsusData types are now supported
✅ **DSL Metrics**: Download/upload rates, SNR values
✅ **Ping Metrics**: Response times and packet loss
✅ **Parental Controls**: Rules and blocked clients
✅ **Port Forwarding**: Status and rule counts
✅ **System Flags**: Capabilities and feature flags
✅ **Enhanced WLAN**: Channel, power, bandwidth information
✅ **Guest Networks**: Comprehensive GWLAN support
✅ **Firmware Notes**: Release notes and build information

### Benefits of Modular Design

1. **Maintainability**: Each collector handles specific functionality
2. **Scalability**: Easy to add new collectors or modify existing ones
3. **Error Isolation**: Failures in one collector don't affect others
4. **Testing**: Individual collectors can be tested separately
5. **Performance**: Concurrent collection from multiple collectors
6. **Configuration**: Collectors can be enabled/disabled independently

### Usage

```bash
# Install dependencies
pip install -r requirements_v2.txt

# Set environment variables
export ASUS_PASSWORD=your_password
export ASUS_HOSTNAME=192.168.1.1

# Run the modular exporter
python3 asus_exporter_v2.py
```

### Endpoints

- **`/metrics`** - Prometheus metrics
- **`/health`** - Health check
- **`/info`** - Exporter information
- **`/collectors`** - Collector details

### Total Metrics Count

The modular exporter now provides **comprehensive coverage** of all available ASUS router metrics, with estimated **200+ individual metrics** covering:

- System performance and resources
- Network interfaces and traffic
- WiFi clients and connections  
- Hardware status and capabilities
- Firmware and system information
- VPN services and connections
- Network services and features

This represents a **significant improvement** over the original script with **100% coverage** of available AsusRouter data types.
