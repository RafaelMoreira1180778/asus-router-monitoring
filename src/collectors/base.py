"""Base collector interface and utilities"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from asusrouter import AsusData, AsusRouter
from asusrouter.config import ARConfig, ARConfigKey
from asusrouter.tools.security import ARSecurityLevel

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Base class for all metric collectors"""

    def __init__(self, router: AsusRouter):
        self.router = router
        self.logger = logging.getLogger(self.__class__.__name__)
        # Initialize secure configuration for debug payload (v1.19.0+)
        self._setup_secure_config()

    @staticmethod
    def _setup_secure_config():
        """Setup secure configuration with ARConfigKey (v1.19.0+)"""
        try:
            # Set debug payload security level to default (blocks sensitive data)
            ARConfig.set(ARConfigKey.DEBUG_PAYLOAD, ARSecurityLevel.DEFAULT)
            logger.debug("Secure configuration initialized with ARConfigKey")
        except Exception as e:
            logger.debug(f"Could not set secure configuration: {e}")

    @abstractmethod
    async def collect(self) -> dict[str, Any]:
        """Collect metrics and return as dict"""
        pass

    @abstractmethod
    def get_data_types(self) -> list[AsusData]:
        """Return list of AsusData types this collector handles"""
        pass

    def flatten_for_info_metric(
        self, data: Any, max_depth: int = 3, current_depth: int = 0
    ) -> dict[str, str]:
        """
        Recursively flatten nested data structures for Prometheus Info metrics.
        Info metrics can only handle string values, so all nested structures must be converted.
        """
        if current_depth >= max_depth:
            return {"value": str(data)}

        if isinstance(data, dict):
            flattened = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    # Flatten nested dict by prefixing keys
                    nested_flat = self.flatten_for_info_metric(value, max_depth, current_depth + 1)
                    if isinstance(nested_flat, dict):
                        for nested_key, nested_value in nested_flat.items():
                            flattened[f"{key}_{nested_key}"] = str(nested_value)
                    else:
                        flattened[key] = str(nested_flat)
                elif isinstance(value, (list, tuple)):
                    # Convert lists to comma-separated strings
                    flattened[key] = ", ".join(str(item) for item in value)
                elif value is None:
                    flattened[key] = "None"
                else:
                    flattened[key] = str(value)
            return flattened
        elif isinstance(data, (list, tuple)):
            return {"value": ", ".join(str(item) for item in data)}
        elif data is None:
            return {"value": "None"}
        else:
            return {"value": str(data)}


class CollectorError(Exception):
    """Exception raised by collectors"""

    pass
