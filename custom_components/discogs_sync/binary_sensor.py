"""Simplified binary sensor platform for Discogs Sync rate limit information."""
from __future__ import annotations

import datetime
from typing import Dict, Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DiscogsRateLimitSensor(coordinator),
        DiscogsAPIStatusSensor(coordinator)
    ])


class DiscogsRateLimitSensor(CoordinatorEntity, BinarySensorEntity):
    """Simplified binary sensor for Discogs API rate limit status."""
    
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_name = "Rate Limit"
    _attr_icon = "mdi:api"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

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
        # If API is disabled, rate limit is not a problem
        if not self.coordinator.is_api_enabled:
            return False
        return self.coordinator.get_rate_limit_data().get("exceeded", False)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Available if API is enabled and we have data, or if API is disabled (to show state)
        if not self.coordinator.is_api_enabled:
            return True  # Show as available but "off" when API disabled
        return self.coordinator.get_rate_limit_data().get("last_updated") is not None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return rate limit attributes."""
        # If API is disabled, show disabled status
        if not self.coordinator.is_api_enabled:
            return {
                "status": "API calls disabled",
                "description": "Rate limit monitoring inactive while API calls are disabled"
            }
            
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


class DiscogsAPIStatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for Discogs API availability status."""
    
    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_name = "API Status"
    _attr_icon = "mdi:api-off"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator):
        """Initialize the API status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_api_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name
        }

    @property
    def is_on(self) -> bool:
        """Return True if API is NOT available (problem state)."""
        # If API is manually disabled, don't show as problem
        if not self.coordinator.is_api_enabled:
            return False  # No problem when manually disabled
            
        api_status = self.coordinator.data.get("api_status", {})
        # Return True (problem) if hello field is NOT defined
        return api_status.get("hello") is None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Available if API is enabled and we have data, or if API is disabled (to show state)
        if not self.coordinator.is_api_enabled:
            return True  # Show as available but "off" when API disabled
        return self.coordinator.data.get("api_status", {}).get("last_checked") is not None

    @property
    def icon(self) -> str:
        """Return the icon based on API status."""
        # Show API off icon when manually disabled
        if not self.coordinator.is_api_enabled:
            return "mdi:api-off"
            
        if self.is_on:  # API is down (problem state)
            return "mdi:api-off"
        else:  # API is up
            return "mdi:api"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return API status attributes."""
        # If API is disabled, show disabled status
        if not self.coordinator.is_api_enabled:
            return {
                "status": "API calls manually disabled",
                "description": "API monitoring inactive while API calls are disabled",
                "last_known_state": "disabled"
            }
            
        api_status = self.coordinator.data.get("api_status", {})
        
        attributes = {}
        
        # Add last checked timestamp
        if last_checked := api_status.get("last_checked"):
            attributes["last_updated"] = datetime.datetime.fromtimestamp(last_checked).strftime('%Y-%m-%d %H:%M:%S')
        
        # Add API version if available
        if api_version := api_status.get("api_version"):
            attributes["api_version"] = api_version
            
        # Add documentation URL if available
        if doc_url := api_status.get("documentation_url"):
            attributes["documentation_url"] = doc_url
            
        # Add statistics if available
        if statistics := api_status.get("statistics"):
            attributes.update({
                "total_releases": statistics.get("releases"),
                "total_artists": statistics.get("artists"), 
                "total_labels": statistics.get("labels")
            })
            
        return attributes