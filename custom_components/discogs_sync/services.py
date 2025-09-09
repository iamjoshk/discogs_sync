"""Simplified services for the Discogs Sync integration."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers.json import save_json

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Simple rate limiting for services
_last_service_calls = {}
_min_service_interval = timedelta(seconds=1)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register simplified services for the Discogs integration."""

    async def download_collection_service(call: ServiceCall) -> Optional[Dict]:
        """Download full collection data."""
        return await _handle_download_service(hass, call, "collection")

    async def download_wantlist_service(call: ServiceCall) -> Optional[Dict]:
        """Download full wantlist data."""
        return await _handle_download_service(hass, call, "wantlist")

    async def download_user_list_service(call: ServiceCall) -> Optional[Dict]:
        """Download user list data."""
        return await _handle_download_service(hass, call, "user_list")

    # Register services
    hass.services.async_register(
        DOMAIN,
        "download_collection",
        download_collection_service,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        "download_wantlist", 
        download_wantlist_service,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        "download_user_list", 
        download_user_list_service,
        supports_response=SupportsResponse.ONLY,
    )


async def _handle_download_service(
    hass: HomeAssistant, 
    call: ServiceCall, 
    service_type: str
) -> Optional[Dict]:
    """Handle download service calls with rate limiting."""
    
    # Check rate limiting
    now = datetime.now()
    last_call = _last_service_calls.get(service_type, datetime.min)
    
    if now - last_call < _min_service_interval:
        time_to_wait = (last_call + _min_service_interval - now).total_seconds()
        return {"error": f"Service called too frequently. Try again in {time_to_wait:.1f} seconds."}
    
    _last_service_calls[service_type] = now
    
    # Get coordinator from any entry (they all use the same API client)
    coordinator = None
    for entry_data in hass.data.get(DOMAIN, {}).values():
        if hasattr(entry_data, 'api_client'):
            coordinator = entry_data
            break
    
    if not coordinator:
        _LOGGER.error("No Discogs coordinator found")
        return {"error": "Discogs integration not configured"}
    
    try:
        # Get data based on service type
        if service_type == "collection":
            # Get folder_id from service call data (defaults to 0 for "All")
            folder_id = call.data.get("folder_id", 0)
            data = await coordinator.get_full_collection(folder_id)
        elif service_type == "wantlist":
            data = await coordinator.get_full_wantlist()
        elif service_type == "user_list":
            # Get list_id from service call data (required)
            list_id = call.data.get("list_id")
            if list_id is None:
                return {"error": "list_id parameter is required for user_list download"}
            data = await coordinator.get_user_list_items(list_id)
        else:
            return {"error": f"Unknown service type: {service_type}"}
        
        # Handle file download if requested
        should_download = call.data.get("download", False)
        if should_download and data:
            filename = f"discogs_{service_type}.json"
            file_path = call.data.get("path", hass.config.path(filename))
            await hass.async_add_executor_job(save_json, file_path, data)
            _LOGGER.info("Saved %d items to %s", len(data), file_path)
        
        # Return data in response
        if data:
            return {service_type: data}
        else:
            # Log when no data is available (e.g., empty folder)
            if service_type == "collection" and call.data.get("folder_id"):
                folder_id = call.data.get("folder_id")
                _LOGGER.warning("No collection data available for folder %s (folder may be empty)", folder_id)
            elif service_type == "user_list":
                list_id = call.data.get("list_id")
                _LOGGER.warning("No user list data available for list %s (list may be empty)", list_id)
            else:
                _LOGGER.warning("No %s data available", service_type)
            return {"error": f"No {service_type} data available"}
        
    except Exception as err:
        _LOGGER.error("Failed to download %s: %s", service_type, err)
        return {"error": f"Failed to download {service_type}: {str(err)}"}
