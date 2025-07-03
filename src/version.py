"""Version information for ASUS Router Prometheus Exporter"""

__version__ = "2.0.0"
__author__ = "Rafael"
__description__ = "High-performance, modular Prometheus exporter for ASUS routers"
__license__ = "MIT"

# Supported Python versions
PYTHON_REQUIRES = ">=3.8"

# Supported AsusRouter library versions
ASUSROUTER_MIN_VERSION = "1.14.0"

# Build information
BUILD_DATE = "2025-07-03"
ARCHITECTURE = "modular"

# Feature flags
FEATURES = {
    "modular_collectors": True,
    "async_collection": True,
    "health_endpoints": True,
    "error_isolation": True,
    "comprehensive_logging": True,
    "docker_support": True,
}

# Collector information
COLLECTORS = {
    "SystemCollector": ["CPU", "RAM", "SYSINFO"],
    "NetworkCollector": ["WAN", "NETWORK"],
    "WiFiCollector": ["CLIENTS", "SYSINFO", "GWLAN", "WLAN"],
    "HardwareCollector": ["PORTS", "TEMPERATURE", "NODE_INFO"],
    "FirmwareCollector": [
        "FIRMWARE",
        "FIRMWARE_NOTE",
        "DEVICEMAP",
        "BOOTTIME",
        "FLAGS",
    ],
    "VPNCollector": ["OPENVPN", "WIREGUARD", "VPNC"],
    "ServicesCollector": [
        "LED",
        "AURA",
        "SPEEDTEST",
        "AIMESH",
        "DSL",
        "PARENTAL_CONTROL",
        "PORT_FORWARDING",
        "PING",
    ],
}

# Total metrics count estimate
ESTIMATED_METRICS_COUNT = 200


def get_version_info():
    """Get comprehensive version information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "license": __license__,
        "build_date": BUILD_DATE,
        "architecture": ARCHITECTURE,
        "python_requires": PYTHON_REQUIRES,
        "asusrouter_min_version": ASUSROUTER_MIN_VERSION,
        "features": FEATURES,
        "collectors": COLLECTORS,
        "estimated_metrics": ESTIMATED_METRICS_COUNT,
    }
