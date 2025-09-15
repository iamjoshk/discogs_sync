"""Simplified binary sensor platform for Discogs Sync rate limit information."""
from __future__ import annotations

import datetime
from typing import Dict, Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DiscogsRateLimitSensor(coordinator)])


class DiscogsRateLimitSensor(CoordinatorEntity, BinarySensorEntity):
    """Simplified binary sensor for Discogs API rate limit status."""
    
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_name = "Rate Limit"
    _attr_icon = "mdi:api"

    def __init__(self, coordinator):
        """Initialize the rate limit sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_rate_limit"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name
        }

    @property
    def is_on(self) -> bool:
        """Return if rate limit is exceeded."""
        return self.coordinator.get_rate_limit_data().get("exceeded", False)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.get_rate_limit_data().get("last_updated") is not None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return rate limit attributes."""
        data = self.coordinator.get_rate_limit_data()
        
        attributes = {
            "total_limit": data.get("total", 60),
            "used": data.get("used", 0),
            "remaining": data.get("remaining", 60),
        }
        
        # Add timestamps and calculations
        if last_updated := data.get("last_updated"):
            attributes["last_updated"] = datetime.datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S')
            
            if data.get("exceeded"):
                reset_time = datetime.datetime.fromtimestamp(last_updated + 60)
                attributes["reset_time"] = reset_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Add percentage used
        if data.get("total", 0) > 0:
            percent_used = round((data.get("used", 0) / data.get("total", 60)) * 100, 1)
            attributes["percent_used"] = f"{percent_used}%"
            
        return attributes
