# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-10-21

Initial release! 🎉

### What's Included

**Core Monitoring**
- 200+ metrics across system, network, WiFi, hardware, VPN, and services
- 7 specialized collectors for modular data collection
- Real-time metric updates with configurable intervals
- Individual collector error isolation

**Dashboard & Visualization**
- Beautiful pre-configured Grafana dashboard
- Prometheus time-series database
- Auto-refresh with historical trends
- Port status monitoring with color coding
- WiFi analytics by band (2.4GHz/5GHz)
- Network traffic graphs with rate calculations

**Infrastructure**
- Docker Compose for easy deployment
- Health check endpoints (`/health`, `/info`, `/collectors`)
- Comprehensive error handling and logging
- Async operations for performance
- Environment-based configuration

**Developer Experience**
- Poetry for dependency management
- Ruff for linting and formatting
- Python 3.12 with modern type hints
- Modular architecture for extensibility
- Clean package structure with proper re-exports

### Tested With
- ASUS routers running [Asuswrt-Merlin](https://www.asuswrt-merlin.net/) firmware
- Compatible with routers supported by [AsusRouter library](https://github.com/Vaskivskyi/asusrouter#supported-devices)

### Requirements
- Python 3.12+
- Docker and Docker Compose
- ASUS router with web interface enabled
- Network access to router

---

*99% vibe coded, as all things should be* ✨
