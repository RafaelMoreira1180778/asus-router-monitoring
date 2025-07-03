"""Base collector interface and utilities"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from asusrouter import AsusData, AsusRouter

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Base class for all metric collectors"""

    def __init__(self, router: AsusRouter):
        self.router = router
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Collect metrics and return as dict"""
        pass

    @abstractmethod
    def get_data_types(self) -> list[AsusData]:
        """Return list of AsusData types this collector handles"""
        pass

    def flatten_for_info_metric(
        self, data: Any, max_depth: int = 3, current_depth: int = 0
    ) -> Dict[str, str]:
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
                    nested_flat = self.flatten_for_info_metric(
                        value, max_depth, current_depth + 1
                    )
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
