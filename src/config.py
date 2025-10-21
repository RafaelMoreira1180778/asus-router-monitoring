"""
Configuration module for the ASUS Router Prometheus Exporter
"""

import logging
import os
from dataclasses import dataclass


@dataclass
class ExporterConfig:
    """Configuration class for the ASUS Router Exporter"""

    # Router connection settings
    hostname: str
    username: str
    password: str
    use_ssl: bool = False

    # Connection resilience settings (v1.19.0+)
    allow_fallback: bool = True
    strict_ssl: bool = False
    allow_upgrade_http_to_https: bool = True

    # Exporter settings
    port: int = 8000
    collection_interval: int = 15

    # Logging settings
    log_level: str = "INFO"

    # Cache settings
    cache_time: int = 5

    @classmethod
    def from_env(cls) -> "ExporterConfig":
        """Create configuration from environment variables"""
        password = os.getenv("ASUS_PASSWORD")
        if not password:
            raise ValueError("ASUS_PASSWORD environment variable is required")

        return cls(
            hostname=os.getenv("ASUS_HOSTNAME", "192.168.1.1"),
            username=os.getenv("ASUS_USERNAME", "admin"),
            password=password,
            use_ssl=os.getenv("ASUS_USE_SSL", "false").lower() == "true",
            allow_fallback=os.getenv("ASUS_ALLOW_FALLBACK", "true").lower() == "true",
            strict_ssl=os.getenv("ASUS_STRICT_SSL", "false").lower() == "true",
            allow_upgrade_http_to_https=os.getenv(
                "ASUS_ALLOW_UPGRADE_HTTP_TO_HTTPS", "true"
            ).lower()
            == "true",
            port=int(os.getenv("EXPORTER_PORT", "8000")),
            collection_interval=int(os.getenv("EXPORTER_COLLECTION_INTERVAL", "15")),
            log_level=os.getenv("EXPORTER_LOG_LEVEL", "INFO").upper(),
            cache_time=int(os.getenv("EXPORTER_CACHE_TIME", "5")),
        )


def setup_logging(log_level: str) -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
