"""Simplified button platform for Discogs integration."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define endpoints with their display names
ENDPOINTS = {
    "collection": "Collection",
    "wantlist": "Wantlist", 
    "collection_value": "Collection Value",
    "random_record": "Random Record",
    "user_lists": "User Lists",
    "user_folders": "User Folders"
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Discogs button entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        DiscogsRefreshButton(coordinator, endpoint, display_name)
        for endpoint, display_name in ENDPOINTS.items()
    ]
    
    async_add_entities(entities)


class DiscogsRefreshButton(CoordinatorEntity, ButtonEntity):
    """Button for refreshing specific Discogs endpoints."""
    _attr_has_entity_name = True
    _attr_entity_category = None
    _attr_icon = "mdi:refresh"
    
    def __init__(self, coordinator, endpoint: str, display_name: str):
        """Initialize the button."""
        super().__init__(coordinator)
        self._endpoint = endpoint
        self._attr_name = f"Refresh {display_name}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{endpoint}_refresh"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name
        }
        
    async def async_press(self):
        """Handle button press."""
        _LOGGER.debug("Refreshing %s endpoint", self._endpoint)
        
        success = await self.coordinator.manual_refresh_endpoint(self._endpoint)
        if not success:
            _LOGGER.warning("Failed to refresh %s endpoint", self._endpoint)