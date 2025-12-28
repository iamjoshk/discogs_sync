"""The Discogs Sync integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_NAME, Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN, DEFAULT_NAME,
    CONF_ENABLE_SCHEDULED_UPDATES,
    CONF_COLLECTION_UPDATE_INTERVAL, CONF_WANTLIST_UPDATE_INTERVAL,
    CONF_COLLECTION_VALUE_UPDATE_INTERVAL, CONF_RANDOM_RECORD_UPDATE_INTERVAL,
    CONF_USER_LISTS_UPDATE_INTERVAL, CONF_USER_FOLDERS_UPDATE_INTERVAL
)
from .coordinator import DiscogsCoordinator
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Discogs from a config entry."""
    # Create the simplified coordinator
    coordinator = DiscogsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Store in hass data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # Register update listener for options
    entry.async_on_unload(entry.add_update_listener(async_options_updated))

    # Set up the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register the simplified services
    await async_register_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Remove data and services
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:  # If it's the last entry, remove the services
            hass.services.async_remove(DOMAIN, "download_collection")
            hass.services.async_remove(DOMAIN, "download_wantlist")
            hass.services.async_remove(DOMAIN, "download_user_list")
            hass.services.async_remove(DOMAIN, "download_image")
            
    return unload_ok

async def async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    # Get the coordinator
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Log the retrieved options
    _LOGGER.debug(
        "Options updated: enable_updates=%s, options=%s",
        entry.options.get(CONF_ENABLE_SCHEDULED_UPDATES),
        entry.options
    )
    
    # Get interval values for each endpoint
    collection_interval = entry.options.get(CONF_COLLECTION_UPDATE_INTERVAL)
    wantlist_interval = entry.options.get(CONF_WANTLIST_UPDATE_INTERVAL) 
    collection_value_interval = entry.options.get(CONF_COLLECTION_VALUE_UPDATE_INTERVAL)
    random_record_interval = entry.options.get(CONF_RANDOM_RECORD_UPDATE_INTERVAL)
    user_lists_interval = entry.options.get(CONF_USER_LISTS_UPDATE_INTERVAL)
    user_folders_interval = entry.options.get(CONF_USER_FOLDERS_UPDATE_INTERVAL)
    
    # Log interval values
    _LOGGER.debug(
        "Update intervals: collection=%s, wantlist=%s, value=%s, random=%s, lists=%s, folders=%s",
        collection_interval,
        wantlist_interval,
        collection_value_interval,
        random_record_interval,
        user_lists_interval,
        user_folders_interval
    )
    
    # Update the coordinator's configuration with the new interval settings
    coordinator.update_intervals(
        collection_interval=collection_interval,
        wantlist_interval=wantlist_interval,
        collection_value_interval=collection_value_interval,
        random_record_interval=random_record_interval,
        user_lists_interval=user_lists_interval,
        user_folders_interval=user_folders_interval
    )
    
    # Update the coordinator's update interval to use the shortest configured interval
    new_update_interval = coordinator._get_update_interval(entry)
    coordinator.update_interval = new_update_interval
    
    # Request a refresh with the new settings
    await coordinator.async_request_refresh()
