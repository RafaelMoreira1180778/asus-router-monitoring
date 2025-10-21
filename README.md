# 📡 ASUS Router Exporter for Prometheus & Grafana

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> *99% vibe coded, as all things should be* ✨

A beautiful Prometheus + Grafana monitoring stack for ASUS routers. Get deep insights into your network with 200+ metrics, zero hassle.

**Tested with**: [Asuswrt-Merlin](https://www.asuswrt-merlin.net/) firmware

## 🚀 What You Get

**System Monitoring**: CPU, RAM, load average, boot time, connection status  
**Network Stats**: WAN/LAN traffic, interface statistics, DNS info  
**WiFi Analytics**: Client tracking, RSSI, TX/RX rates, band analysis  
**Hardware Health**: Port monitoring, temperature sensors, link speeds  
**VPN Status**: OpenVPN, WireGuard, VPNC monitoring  
**Services**: LED, Aura lighting, speedtest, firmware updates, and more

All wrapped in a beautiful Grafana dashboard with real-time updates.

## 📸 Screenshots

![Dashboard Overview](img/dashboard_1.png)
![Network & WiFi Analytics](img/dashboard_2.png)
![Hardware & System Health](img/dashboard_3.png)

## 📋 What You Need

- Docker and Docker Compose
- ASUS router with web interface enabled
- Network access to your router

## 🛠️ Quick Start

```bash
# Clone and configure
git clone https://github.com/your-username/asus-router-monitoring.git
cd asus-router-monitoring
cp .env.example .env

# Edit .env with your router details
nano .env

# Start everything
docker-compose up -d
```

**That's it!** 🎉

Access your dashboards:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Metrics**: http://localhost:8000/metrics

## ⚙️ Configuration

Edit `.env` with your router details:

```bash
ASUS_HOSTNAME=192.168.1.1
ASUS_USERNAME=admin
ASUS_PASSWORD=your_router_password
ASUS_USE_SSL=false

# Optional tweaks
EXPORTER_COLLECTION_INTERVAL=15  # How often to collect metrics (seconds)
EXPORTER_LOG_LEVEL=INFO          # DEBUG for troubleshooting
```

## 🔍 Troubleshooting

**Connection issues?**
```bash
curl http://localhost:8000/health  # Check exporter health
docker-compose logs asus-exporter  # View logs
```

**No data in Grafana?**
- Check Prometheus targets: http://localhost:9090/targets
- Verify router credentials in `.env`
- Some metrics depend on your router model/firmware

**Still stuck?**
- Set `EXPORTER_LOG_LEVEL=DEBUG` in `.env`
- Check [AsusRouter compatibility](https://github.com/Vaskivskyi/asusrouter#supported-devices)

## 📚 Built With

- **[AsusRouter](https://github.com/Vaskivskyi/asusrouter)** - Python library for ASUS router API
- **[Asuswrt-Merlin](https://www.asuswrt-merlin.net/)** - Enhanced firmware (recommended)
- **[Prometheus](https://prometheus.io/)** - Metrics collection and storage
- **[Grafana](https://grafana.com/)** - Beautiful dashboards and visualization
- **[Docker](https://www.docker.com/)** - Containerization magic

## 📋 License

MIT License - See [LICENSE](LICENSE) for details.

---

Made with ☕ and ✨ for the ASUS router community
