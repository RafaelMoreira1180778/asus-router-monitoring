# ASUS Router Monitoring Stack

A comprehensive monitoring solution for ASUS routers using Prometheus, Grafana, and a custom Python exporter. This stack provides real-time visualization of router performance, network traffic, system health, and hardware metrics.

## 📖 Overview

This project provides a complete monitoring solution for ASUS routers, featuring:

- **🔍 Comprehensive Metrics**: CPU, RAM, network traffic, WiFi clients, temperatures, ports, and more
- **📊 Beautiful Dashboards**: Pre-configured Grafana dashboards with real-time visualizations
- **🐳 Easy Deployment**: Docker Compose stack with persistent storage and health checks
- **🔧 Production Ready**: Secure, scalable, and maintainable monitoring infrastructure
- **🐍 Python 3.12+**: Modern Python with robust error handling and async operations

**Tested with**: ASUS AX-series routers (see [compatibility list](https://github.com/Vaskivskyi/asusrouter#supported-devices))

## 🚀 Features

### Router Metrics
- **System Performance**: CPU usage, load average, memory utilization
- **Network Traffic**: WAN/LAN traffic rates, bytes transferred, port status
- **Hardware Monitoring**: Temperature sensors, port link rates, connection status
- **WiFi Analytics**: Client counts by band, association statistics
- **System Services**: VPN status, LED status, firmware information
- **Storage**: NVRAM usage, JFFS filesystem statistics

### Monitoring Stack
- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Advanced dashboards with beautiful visualizations
- **Docker Compose**: Easy deployment with persistent volumes
- **Health Checks**: Built-in monitoring of all components

## 📋 Prerequisites

- **Docker and Docker Compose**
- **Python 3.12+** (for local development/testing)
- ASUS router with web interface enabled
- Network access to your router
- At least 1GB free disk space for metrics storage

## 🛠️ Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/RafaelMoreira1180778/asus-router-monitoring.git
cd asus-router-monitoring

# Copy the environment template
cp .env.example .env

# Edit the configuration file
nano .env
```

### 2. Configure Your Router

Edit `.env` with your router details:

```bash
# Router connection settings
ASUS_HOSTNAME=192.168.1.1
ASUS_USERNAME=admin
ASUS_PASSWORD=your_actual_router_password
ASUS_USE_SSL=false

# Optional: Customize ports and settings
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
EXPORTER_PORT=8000
```

### 3. Start the Monitoring Stack

```bash
# Build and start all services
docker-compose up -d

# Check the status of all services
docker-compose ps

# View logs if needed
docker-compose logs -f asus-exporter
```

### 4. Access the Dashboards

- **Grafana**: http://localhost:3000 (admin/admin - change in .env)
- **Prometheus**: http://localhost:9090
- **Exporter**: http://localhost:8000/metrics

## 🐍 Local Development (Python 3.12+)

For development or running without Docker:

### 1. Setup Python Environment

```bash
# Ensure Python 3.12+ is installed
python3 --version

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Test Router Connection

```bash
# Set environment variables
export ASUS_HOSTNAME=192.168.1.1
export ASUS_USERNAME=admin
export ASUS_PASSWORD=your_password

# Test connection
python3 test_connection.py
```

### 3. Run Exporter Locally

```bash
# Start the exporter
python3 asus_exporter.py

# Or use the startup script
./start_exporter.sh
```

The exporter will be available at: http://localhost:8000/metrics

## 📊 Available Metrics

### System Metrics
| Metric Name                   | Description                       | Type  |
| ----------------------------- | --------------------------------- | ----- |
| `asus_cpu_usage_percent`      | CPU usage percentage              | Gauge |
| `asus_load_average`           | System load average (1m, 5m, 15m) | Gauge |
| `asus_connection_status`      | Router connection status          | Gauge |
| `asus_boot_timestamp_seconds` | Router boot timestamp             | Gauge |

### Memory Metrics
| Metric Name                | Description           | Type  |
| -------------------------- | --------------------- | ----- |
| `asus_ram_used_bytes`      | RAM used in bytes     | Gauge |
| `asus_ram_free_bytes`      | RAM free in bytes     | Gauge |
| `asus_ram_total_bytes`     | RAM total in bytes    | Gauge |
| `asus_ram_usage_percent`   | RAM usage percentage  | Gauge |
| `asus_ram_buffers_bytes`   | RAM buffers in bytes  | Gauge |
| `asus_ram_cache_bytes`     | RAM cache in bytes    | Gauge |
| `asus_nvram_used_bytes`    | NVRAM used in bytes   | Gauge |
| `asus_jffs_free_megabytes` | JFFS free space in MB | Gauge |

### Network Metrics
| Metric Name                      | Description        | Type    | Labels      |
| -------------------------------- | ------------------ | ------- | ----------- |
| `asus_wan_rx_bytes_total`        | WAN RX bytes total | Counter | -           |
| `asus_wan_tx_bytes_total`        | WAN TX bytes total | Counter | -           |
| `asus_wan_rx_rate_bytes_per_sec` | WAN RX rate        | Gauge   | -           |
| `asus_wan_tx_rate_bytes_per_sec` | WAN TX rate        | Gauge   | -           |
| `asus_interface_rx_bytes_total`  | Interface RX bytes | Counter | `interface` |
| `asus_interface_tx_bytes_total`  | Interface TX bytes | Counter | `interface` |

### Port Metrics
| Metric Name                | Description                | Type  | Labels                 |
| -------------------------- | -------------------------- | ----- | ---------------------- |
| `asus_port_status`         | Port status (1=up, 0=down) | Gauge | `port_type`, `port_id` |
| `asus_port_link_rate_mbps` | Port link rate in Mbps     | Gauge | `port_type`, `port_id` |

### WiFi Metrics
| Metric Name                       | Description           | Type  | Labels |
| --------------------------------- | --------------------- | ----- | ------ |
| `asus_wifi_clients_total`         | Total WiFi clients    | Gauge | -      |
| `asus_wifi_clients_by_band`       | Clients by WiFi band  | Gauge | `band` |
| `asus_wifi_clients_associated`    | Associated clients    | Gauge | `band` |
| `asus_wifi_clients_authorized`    | Authorized clients    | Gauge | `band` |
| `asus_wifi_clients_authenticated` | Authenticated clients | Gauge | `band` |

### Hardware Metrics
| Metric Name                | Description         | Type  | Labels   |
| -------------------------- | ------------------- | ----- | -------- |
| `asus_temperature_celsius` | Temperature sensors | Gauge | `sensor` |

### Service Metrics
| Metric Name                      | Description               | Type  | Labels      |
| -------------------------------- | ------------------------- | ----- | ----------- |
| `asus_firmware_update_available` | Firmware update available | Gauge | -           |
| `asus_led_status`                | LED status                | Gauge | -           |
| `asus_aura_status`               | Aura lighting status      | Gauge | -           |
| `asus_openvpn_client_status`     | OpenVPN client status     | Gauge | `client_id` |
| `asus_openvpn_server_status`     | OpenVPN server status     | Gauge | `server_id` |

### Connection Metrics
| Metric Name               | Description                | Type  |
| ------------------------- | -------------------------- | ----- |
| `asus_connections_total`  | Total network connections  | Gauge |
| `asus_connections_active` | Active network connections | Gauge |

### Collection Metrics
| Metric Name                              | Description                | Type      | Labels       |
| ---------------------------------------- | -------------------------- | --------- | ------------ |
| `asus_collection_duration_seconds`       | Collection time histogram  | Histogram | -            |
| `asus_collection_errors_total`           | Total collection errors    | Counter   | `error_type` |
| `asus_last_collection_timestamp_seconds` | Last successful collection | Gauge     | -            |

## 🔧 Configuration

### Environment Variables

| Variable                       | Default       | Description                             |
| ------------------------------ | ------------- | --------------------------------------- |
| `ASUS_HOSTNAME`                | `192.168.1.1` | Router IP address                       |
| `ASUS_USERNAME`                | `admin`       | Router username                         |
| `ASUS_PASSWORD`                | _(required)_  | Router password                         |
| `ASUS_USE_SSL`                 | `false`       | Use HTTPS for router                    |
| `EXPORTER_PORT`                | `8000`        | Exporter port                           |
| `EXPORTER_LOG_LEVEL`           | `INFO`        | Log level (DEBUG, INFO, WARNING, ERROR) |
| `EXPORTER_COLLECTION_INTERVAL` | `15`          | Collection interval in seconds          |
| `PROMETHEUS_PORT`              | `9090`        | Prometheus port                         |
| `PROMETHEUS_RETENTION_TIME`    | `15d`         | Data retention period                   |
| `GRAFANA_PORT`                 | `3000`        | Grafana port                            |
| `GRAFANA_ADMIN_USER`           | `admin`       | Grafana admin username                  |
| `GRAFANA_ADMIN_PASSWORD`       | `admin`       | Grafana admin password                  |
| `TZ`                           | `UTC`         | Timezone                                |

### Customizing Collection Interval

You can adjust how frequently metrics are collected:

```bash
# In .env file
EXPORTER_COLLECTION_INTERVAL=30  # Collect every 30 seconds
PROMETHEUS_SCRAPE_INTERVAL=60s   # Scrape every 60 seconds
```

## 📈 Grafana Dashboard

The included dashboard provides:

- **System Overview**: Connection status, CPU, RAM usage
- **Network Traffic**: Real-time WAN traffic with rate graphs
- **WiFi Analytics**: Client counts and connection statistics
- **Hardware Health**: Temperature monitoring and port status
- **Memory Details**: Breakdown of RAM, cache, buffers, and storage
- **Long-term Trends**: Historical data with configurable time ranges

### Dashboard Features
- Auto-refresh every 30 seconds
- Responsive design for mobile and desktop
- Drill-down capabilities for detailed analysis
- Alert-ready queries for threshold monitoring

## 🔍 Troubleshooting

### Connection Issues

1. **Check router connectivity**:
   ```bash
   # Test basic connectivity
   ping 192.168.1.1
   
   # Test web interface
   curl -u admin:password http://192.168.1.1
   ```

2. **Verify exporter logs**:
   ```bash
   docker-compose logs asus-exporter
   ```

3. **Check router compatibility**:
   Visit the [AsusRouter compatibility list](https://github.com/Vaskivskyi/asusrouter#supported-devices)

### Service Health

```bash
# Check all services
docker-compose ps

# View specific service logs
docker-compose logs prometheus
docker-compose logs grafana

# Restart services if needed
docker-compose restart asus-exporter
```

### Data Issues

1. **No metrics in Grafana**:
   - Check Prometheus targets: http://localhost:9090/targets
   - Verify exporter health: http://localhost:8000/health
   - Check Grafana datasource configuration

2. **Missing specific metrics**:
   - Some metrics depend on router model and firmware
   - Check exporter logs for unsupported features
   - Verify router permissions and API access

### Performance Tuning

1. **High memory usage**:
   ```bash
   # Reduce Prometheus retention
   PROMETHEUS_RETENTION_TIME=7d
   
   # Increase collection interval
   EXPORTER_COLLECTION_INTERVAL=60
   ```

2. **Slow response times**:
   ```bash
   # Reduce log level
   EXPORTER_LOG_LEVEL=WARNING
   
   # Check router load and network latency
   ```

## 🛡️ Security Considerations

1. **Change default passwords**:
   ```bash
   # In .env file
   GRAFANA_ADMIN_PASSWORD=your_secure_password
   GRAFANA_SECRET_KEY=your_random_secret_key
   ```

2. **Network security**:
   - Run on internal networks only
   - Use HTTPS for production deployments
   - Consider VPN access for remote monitoring

3. **Router credentials**:
   - Use dedicated monitoring account if available
   - Limit router admin access
   - Regularly rotate passwords

## 🔄 Maintenance

### Backup Configuration

```bash
# Backup Grafana data
docker-compose exec grafana tar czf - /var/lib/grafana | gzip > grafana-backup.tar.gz

# Backup Prometheus data
docker-compose exec prometheus tar czf - /prometheus | gzip > prometheus-backup.tar.gz
```

### Updates

```bash
# Update the monitoring stack
docker-compose pull
docker-compose up -d

# View updated services
docker-compose ps
```

### Log Rotation

```bash
# Configure Docker log rotation
echo '{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}' | sudo tee /etc/docker/daemon.json

sudo systemctl restart docker
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines:

1. Test with your router model
2. Add documentation for new metrics
3. Follow the existing code style
4. Update the README for new features

## 📚 Additional Resources

- [AsusRouter Library Documentation](https://github.com/Vaskivskyi/asusrouter)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Acknowledgments

This project uses the following open-source libraries:
- **AsusRouter**: [Vaskivskyi/asusrouter](https://github.com/Vaskivskyi/asusrouter) (MIT License)
- **Prometheus**: [prometheus.io](https://prometheus.io/) (Apache License 2.0)
- **Grafana**: [grafana.com](https://grafana.com/) (AGPLv3 License)

---

**Note**: This monitoring solution provides extensive metrics collection. Some features may not be available on all router models. Check the AsusRouter compatibility list for your specific model.
