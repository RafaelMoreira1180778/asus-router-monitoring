"""Firmware and system information collector"""

from typing import Any

from asusrouter import AsusData

from ..metrics.prometheus_metrics import (
    BOOTTIME,
    COLLECTION_ERRORS_TOTAL,
    DEVICE_MAP_INFO,
    FIRMWARE_BUILD_INFO,
    FIRMWARE_INFO,
    FIRMWARE_RELEASE_NOTES,
    FIRMWARE_UPDATE_AVAILABLE,
    ROUTER_INFO,
    SYSTEM_FLAGS,
)
from .base import BaseCollector


class FirmwareCollector(BaseCollector):
    """Collects firmware and system information"""

    def get_data_types(self) -> list[AsusData]:
        return [
            AsusData.FIRMWARE,
            AsusData.FIRMWARE_NOTE,
            AsusData.DEVICEMAP,
            AsusData.BOOTTIME,
            AsusData.FLAGS,
        ]

    async def collect(self) -> dict[str, Any]:
        """Collect firmware and system info metrics"""
        metrics = {}

        try:
            await self._collect_firmware_metrics(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect firmware data: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="firmware").inc()

        try:
            await self._collect_device_info(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect device info: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="device_info").inc()

        try:
            await self._collect_system_flags(metrics)
        except Exception as e:
            self.logger.debug(f"Failed to collect system flags: {e}")
            COLLECTION_ERRORS_TOTAL.labels(error_type="system_flags").inc()

        return metrics

    async def _collect_firmware_metrics(self, metrics: dict[str, Any]):
        """Collect firmware metrics"""
        firmware_data = await self.router.async_get_data(AsusData.FIRMWARE)
        if firmware_data:
            # Firmware info
            if "current" in firmware_data:
                FIRMWARE_INFO.info(
                    {
                        "current": str(firmware_data.get("current", "unknown")),
                        "available": str(firmware_data.get("available", "none")),
                        "state": str(firmware_data.get("state", "unknown")),
                    }
                )
                metrics["firmware_current"] = firmware_data.get("current")
                metrics["firmware_available"] = firmware_data.get("available")

            # Update availability
            if "state" in firmware_data:
                update_available = 1 if firmware_data["state"] else 0
                FIRMWARE_UPDATE_AVAILABLE.set(update_available)
                metrics["firmware_update_available"] = update_available

            # Build information
            if "build" in firmware_data:
                flattened_build = self.flatten_for_info_metric(firmware_data["build"])
                FIRMWARE_BUILD_INFO.info(flattened_build)

            self.logger.debug("Collected firmware metrics")

        # Firmware release notes
        try:
            firmware_notes = await self.router.async_get_data(AsusData.FIRMWARE_NOTE)
            if firmware_notes:
                flattened_notes = self.flatten_for_info_metric(firmware_notes)
                FIRMWARE_RELEASE_NOTES.info(flattened_notes)
                self.logger.debug("Collected firmware release notes")
        except Exception as e:
            self.logger.debug(f"Firmware notes not available: {e}")

    async def _collect_device_info(self, metrics: dict[str, Any]):
        """Collect device information"""
        try:
            device_data = await self.router.async_get_data(AsusData.DEVICEMAP)
            if device_data:
                router_info = {
                    "model": str(device_data.get("model", "unknown")),
                    "firmware": str(device_data.get("firmware", "unknown")),
                    "hostname": "unknown",  # Will be set from config
                    "brand": str(device_data.get("brand", "ASUSTek")),
                }
                ROUTER_INFO.info(router_info)
                metrics["router_model"] = router_info["model"]
                metrics["router_firmware"] = router_info["firmware"]

                # Convert complex data structures to strings for Info metric
                flattened_data = self.flatten_for_info_metric(device_data)
                DEVICE_MAP_INFO.info(flattened_data)

                self.logger.debug(
                    f"Router model: {router_info['model']}, firmware: {router_info['firmware']}"
                )
        except Exception as e:
            self.logger.debug(f"Device map metrics not available: {e}")

        # Boot time
        try:
            boot_data = await self.router.async_get_data(AsusData.BOOTTIME)
            if boot_data and "timestamp" in boot_data:
                BOOTTIME.set(boot_data["timestamp"])
                metrics["boot_timestamp"] = boot_data["timestamp"]
                self.logger.debug("Collected boot time")
        except Exception as e:
            self.logger.debug(f"Boot time not available: {e}")

    async def _collect_system_flags(self, metrics: dict[str, Any]):
        """Collect system flags and capabilities"""
        try:
            flags_data = await self.router.async_get_data(AsusData.FLAGS)
            if flags_data:
                flattened_flags = self.flatten_for_info_metric(flags_data)
                SYSTEM_FLAGS.info(flattened_flags)
                metrics["system_flags_count"] = len(flags_data)
                self.logger.debug("Collected system flags and capabilities")
        except Exception as e:
            self.logger.debug(f"System flags metrics not available: {e}")
