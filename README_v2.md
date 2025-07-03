# ASUS Router Prometheus Exporter v2.0

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Prometheus](https://img.shields.io/badge/prometheus-compatible-orange.svg)](https://prometheus.io/)

A high-performance, modular Prometheus exporter for ASUS routers with comprehensive monitoring capabilities and modern architecture.

## 🎯 Features

### ✨ Complete Monitoring Coverage
- **🖥️ System Metrics**: CPU, RAM, load average, boot time
- **🌐 Network Monitoring**: WAN/LAN traffic, interface statistics, DNS info  
- **📡 WiFi Analytics**: Client tracking, RSSI, TX/RX rates, band analysis
- **🔌 Hardware Status**: Port monitoring, temperature sensors, capabilities
- **⚙️ Firmware & System**: Version tracking, update availability, system flags
- **🔒 VPN Services**: OpenVPN, WireGuard, VPNC status and statistics
- **🛠️ Additional Services**: LED, Aura lighting, speedtest, AiMesh, DSL, parental controls

### 🏗️ Modern Architecture
- **Modular Design**: 7 specialized collectors for focused functionality
- **Async Operations**: High-performance concurrent data collection
- **Error Isolation**: Individual collector failures don't affect others
- **Comprehensive Logging**: Detailed debugging and monitoring
- **Health Endpoints**: Built-in health checks and service monitoring

### 📈 Enhanced Metrics (200+ Available)
- **Real-time Client Data**: Individual TX/RX rates, connection types, online status
- **Advanced Port Monitoring**: Link capabilities, maximum rates, node-level information
- **VPN Traffic Statistics**: Detailed connection metrics for all VPN types
- **Guest Network Support**: Comprehensive WLAN and Guest WLAN monitoring
- **System Capabilities**: Hardware features, supported services, configuration flags

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Set your router password
export ASUS_PASSWORD="your_router_password"

# Run with Docker
docker run -d \
  --name asus-exporter \
  -p 8000:8000 \
  -e ASUS_PASSWORD="$ASUS_PASSWORD" \
  -e ASUS_HOSTNAME="192.168.1.1" \
  asus-router-exporter:latest

# Check status
curl http://localhost:8000/health
```

### Using Docker Compose (Full Stack)

```bash
# Clone repository
git clone <repository-url>
cd asus-router-monitoring

# Configure environment
cp .env.example .env
echo "ASUS_PASSWORD=your_router_password" >> .env

# Start the complete monitoring stack
make compose-up

# Access services
# - Exporter: http://localhost:8000
# - Prometheus: http://localhost:9090  
# - Grafana: http://localhost:3000
```

### Local Development

```bash
# Install dependencies
make install

# Run locally
ASUS_PASSWORD="your_password" make run
```

## 📊 Endpoints

| Endpoint      | Description                    |
| ------------- | ------------------------------ |
| `/metrics`    | Prometheus metrics             |
| `/health`     | Health check                   |
| `/info`       | Exporter overview and features |
| `/collectors` | Detailed collector information |

## ⚙️ Configuration

### Environment Variables

| Variable                       | Default       | Description                   |
| ------------------------------ | ------------- | ----------------------------- |
| `ASUS_HOSTNAME`                | `192.168.1.1` | Router IP address             |
| `ASUS_USERNAME`                | `admin`       | Router username               |
| `ASUS_PASSWORD`                | *required*    | Router password               |
| `ASUS_USE_SSL`                 | `false`       | Use HTTPS connection          |
| `EXPORTER_PORT`                | `8000`        | HTTP server port              |
| `EXPORTER_COLLECTION_INTERVAL` | `15`          | Collection interval (seconds) |
| `EXPORTER_LOG_LEVEL`           | `INFO`        | Logging level                 |
| `EXPORTER_CACHE_TIME`          | `5`           | Data cache time (seconds)     |

### Example .env file

```bash
ASUS_HOSTNAME=192.168.1.1
ASUS_USERNAME=admin
ASUS_PASSWORD=your_secure_password
ASUS_USE_SSL=false
EXPORTER_PORT=8000
EXPORTER_COLLECTION_INTERVAL=15
EXPORTER_LOG_LEVEL=INFO
```

## 🏗️ Architecture

### Modular Collector System

```
src/
├── collectors/
│   ├── system.py          # CPU, RAM, system info
│   ├── network.py         # WAN, LAN, interface stats
│   ├── wifi.py            # WiFi clients, bands, guest networks
│   ├── hardware.py        # Ports, temperature, node info
│   ├── firmware.py        # Firmware, device info, system flags
│   ├── vpn.py             # OpenVPN, WireGuard, VPNC
│   └── services.py        # LED, Aura, speedtest, misc services
├── metrics/
│   └── prometheus_metrics.py  # Metric definitions
├── server/
│   └── __init__.py        # HTTP server
├── config.py              # Configuration management
└── main.py                # Application entry point
```

### Data Coverage

**34 AsusData Types Supported:**
- AIMESH, AURA, BOOTTIME, CLIENTS, CPU, DEVICEMAP
- DSL, FIRMWARE, FIRMWARE_NOTE, FLAGS, GWLAN, LED
- NETWORK, NODE_INFO, OPENVPN, PARENTAL_CONTROL, PING
- PORT_FORWARDING, PORTS, RAM, SPEEDTEST, SYSINFO
- SYSTEM, TEMPERATURE, VPNC, WAN, WIREGUARD, WLAN
- And more...

## 🔧 Development

### Available Commands

```bash
make help              # Show available commands
make install           # Install dependencies
make lint              # Run linting checks  
make clean             # Clean temporary files
make docker-build      # Build Docker image
make docker-run        # Run Docker container
make compose-up        # Start full stack
make tree              # Show project structure
```

### Adding New Collectors

1. Create collector in `src/collectors/`
2. Inherit from `BaseCollector`
3. Implement `collect()` and `get_data_types()` methods
4. Add to `MetricsCollectorManager`
5. Define metrics in `prometheus_metrics.py`

### Example Collector

```python
from .base import BaseCollector
from asusrouter import AsusData

class MyCollector(BaseCollector):
    def get_data_types(self) -> list[AsusData]:
        return [AsusData.EXAMPLE]
    
    async def collect(self) -> Dict[str, Any]:
        data = await self.router.async_get_data(AsusData.EXAMPLE)
        # Process and return metrics
        return {"my_metric": data}
```

## 📋 Requirements

- **Python 3.8+**
- **AsusRouter library 1.14.0+**
- **Prometheus Client 0.19.0+**
- **aiohttp 3.9.0+**
- **Docker** (for containerized deployment)

## 🤝 Compatibility

Tested with ASUS routers running:
- **AsusWRT firmware**
- **AsusWRT-Merlin firmware**

See [AsusRouter compatibility list](https://github.com/Vaskivskyi/asusrouter#supported-devices) for specific models.

## 📈 Monitoring Integration

### Prometheus Configuration

```yaml
scrape_configs:
  - job_name: 'asus-router'
    static_configs:
      - targets: ['asus-exporter:8000']
    scrape_interval: 30s
```

### Sample Grafana Queries

```promql
# CPU Usage
asus_cpu_usage_percent

# WiFi Clients by Band  
sum by (band) (asus_wifi_clients_by_band)

# WAN Traffic Rate
rate(asus_wan_rx_bytes_total[5m]) * 8 / 1000000

# Port Status Summary
count by (port_type) (asus_port_status == 1)
```

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**
- Verify router IP and credentials
- Check network connectivity
- Ensure router web interface is enabled

**Missing Metrics**
- Check collector logs for specific errors
- Verify router firmware version compatibility
- Review `/collectors` endpoint for supported features

**High Memory Usage**
- Increase `EXPORTER_COLLECTION_INTERVAL`
- Reduce `EXPORTER_CACHE_TIME`
- Monitor Docker container resources

### Debug Mode

```bash
EXPORTER_LOG_LEVEL=DEBUG python asus_exporter.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [AsusRouter Library](https://github.com/Vaskivskyi/asusrouter) by Vaskivskyi
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [aiohttp](https://docs.aiohttp.org/) for async HTTP operations

## 📊 Metrics Overview

The exporter provides comprehensive monitoring with 200+ metrics across:

- **System Performance**: 15+ CPU, memory, and load metrics
- **Network Traffic**: 20+ interface and WAN statistics  
- **WiFi Analytics**: 25+ client and band metrics
- **Hardware Status**: 30+ port and temperature readings
- **Service Monitoring**: 40+ VPN, LED, and system service metrics
- **Advanced Features**: 60+ detailed client, node, and capability metrics

For detailed metrics documentation, visit `/info` endpoint when running.
