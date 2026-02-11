"""Switch platform for Discogs Sync API control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_ENABLE_API_CALLS, ICON_API, ICON_API_OFF

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        DiscogsAPIControlSwitch(coordinator),
    ])


class DiscogsAPIControlSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable Discogs API calls."""
    
    _attr_has_entity_name = True
    _attr_name = "API Control"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator):
        """Initialize the API control switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_api_control"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name
        }

    @property
    def is_on(self) -> bool:
        """Return True if API calls are enabled."""
        return self.coordinator.is_api_enabled
    
    @property
    def icon(self) -> str:
        """Return icon based on switch state."""
        return ICON_API if self.is_on else ICON_API_OFF
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "description": "Controls whether the integration makes API calls to Discogs",
            "usage": "Disable when editing dashboards or to prevent excessive API usage",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the API calls on."""
        await self.coordinator.async_set_api_enabled(True)
        self.async_write_ha_state()
        _LOGGER.info("Discogs API calls enabled")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the API calls off."""
        await self.coordinator.async_set_api_enabled(False)
        self.async_write_ha_state()
        _LOGGER.info("Discogs API calls disabled")