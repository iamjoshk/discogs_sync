"""Simplified data coordinator for Discogs Sync."""
import logging
import time
from datetime import timedelta
from typing import Dict, Any, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN, CONF_NAME

from .const import (
    DOMAIN, DEFAULT_NAME,
    CONF_COLLECTION_UPDATE_INTERVAL, DEFAULT_COLLECTION_UPDATE_INTERVAL,
    CONF_WANTLIST_UPDATE_INTERVAL, DEFAULT_WANTLIST_UPDATE_INTERVAL,
    CONF_COLLECTION_VALUE_UPDATE_INTERVAL, DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL,
    CONF_RANDOM_RECORD_UPDATE_INTERVAL, DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL,
    CONF_USER_LISTS_UPDATE_INTERVAL, DEFAULT_USER_LISTS_UPDATE_INTERVAL,
    CONF_USER_FOLDERS_UPDATE_INTERVAL, DEFAULT_USER_FOLDERS_UPDATE_INTERVAL
)
from .api_client import DiscogsAPIClient

_LOGGER = logging.getLogger(__name__)


class DiscogsCoordinator(DataUpdateCoordinator):
    """Simplified coordinator to fetch Discogs data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize coordinator."""
        self.config_entry = entry
        self.api_client = DiscogsAPIClient(entry.data[CONF_TOKEN])
        self.display_name = entry.data.get(CONF_NAME, DEFAULT_NAME)
        
        # Initialize data structure
        self._data = {
            "user": None,
            "collection_count": 0,
            "wantlist_count": 0,
            "collection_value": {"min": 0, "median": 0, "max": 0, "currency": "$"},
            "random_record": {"title": None, "data": {}},
            "user_lists": {"count": 0, "lists": []},
            "user_folders": {"count": 0, "folders": []},
            "random_record_folder_selection": entry.data.get("random_record_folder_selection", "All"),  # Restore from config entry
            "random_record_folder_id": entry.data.get("random_record_folder_id", 0),  # Restore from config entry
            "last_updated": {}
        }
        
        # Set up endpoint intervals (in minutes) using proper defaults
        self._endpoint_intervals = {
            "collection": entry.options.get(CONF_COLLECTION_UPDATE_INTERVAL, DEFAULT_COLLECTION_UPDATE_INTERVAL),
            "wantlist": entry.options.get(CONF_WANTLIST_UPDATE_INTERVAL, DEFAULT_WANTLIST_UPDATE_INTERVAL),
            "collection_value": entry.options.get(CONF_COLLECTION_VALUE_UPDATE_INTERVAL, DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL),
            "random_record": entry.options.get(CONF_RANDOM_RECORD_UPDATE_INTERVAL, DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL),
            "user_lists": entry.options.get(CONF_USER_LISTS_UPDATE_INTERVAL, DEFAULT_USER_LISTS_UPDATE_INTERVAL),
            "user_folders": entry.options.get(CONF_USER_FOLDERS_UPDATE_INTERVAL, DEFAULT_USER_FOLDERS_UPDATE_INTERVAL)
        }
        
        _LOGGER.debug("Initialized coordinator with intervals: %s", self._endpoint_intervals)
        
        # Set update interval based on configuration
        update_interval = self._get_update_interval(entry)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
    
    def _get_update_interval(self, entry: ConfigEntry) -> timedelta:
        """Get update interval from configuration."""
        # Use shortest configured interval (excluding disabled ones) or default to 10 minutes
        intervals = []
        
        for option_key, default in [
            (CONF_COLLECTION_UPDATE_INTERVAL, DEFAULT_COLLECTION_UPDATE_INTERVAL),
            (CONF_WANTLIST_UPDATE_INTERVAL, DEFAULT_WANTLIST_UPDATE_INTERVAL),
            (CONF_COLLECTION_VALUE_UPDATE_INTERVAL, DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL),
            (CONF_RANDOM_RECORD_UPDATE_INTERVAL, DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL),
            (CONF_USER_LISTS_UPDATE_INTERVAL, DEFAULT_USER_LISTS_UPDATE_INTERVAL),
            (CONF_USER_FOLDERS_UPDATE_INTERVAL, DEFAULT_USER_FOLDERS_UPDATE_INTERVAL)
        ]:
            interval = entry.options.get(option_key, default)
            if interval > 0:  # Only include enabled endpoints
                intervals.append(interval)
        
        min_interval = min(intervals) if intervals else 10
        return timedelta(minutes=max(min_interval, 1))  # At least 1 minute
    
    def update_intervals(self, collection_interval=None, wantlist_interval=None, 
                        collection_value_interval=None, random_record_interval=None,
                        user_lists_interval=None, user_folders_interval=None):
        """Update the individual endpoint intervals."""
        # Store intervals, allowing 0 to disable endpoints
        self._endpoint_intervals = {
            "collection": collection_interval if collection_interval is not None else DEFAULT_COLLECTION_UPDATE_INTERVAL,
            "wantlist": wantlist_interval if wantlist_interval is not None else DEFAULT_WANTLIST_UPDATE_INTERVAL,
            "collection_value": collection_value_interval if collection_value_interval is not None else DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL,
            "random_record": random_record_interval if random_record_interval is not None else DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL,
            "user_lists": user_lists_interval if user_lists_interval is not None else DEFAULT_USER_LISTS_UPDATE_INTERVAL,
            "user_folders": user_folders_interval if user_folders_interval is not None else DEFAULT_USER_FOLDERS_UPDATE_INTERVAL
        }
        
        _LOGGER.debug("Updated endpoint intervals: %s", self._endpoint_intervals)
    
    @property  
    def display_name_property(self) -> str:
        """Return coordinator display name."""
        return self.display_name
    
    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from Discogs."""
        if not self.config_entry.options.get("enable_scheduled_updates", True):
            _LOGGER.debug("Automatic updates disabled")
            return self._data
        
        _LOGGER.debug("Starting data update. Current intervals: %s", self._endpoint_intervals)
        
        try:
            # Get user identity first for username and currency
            identity = await self.hass.async_add_executor_job(self.api_client.get_user_identity)
            if identity:
                username = identity["username"]
                self._data["user"] = username
                self._data["collection_value"]["currency"] = identity["currency"]
                
                _LOGGER.debug("Got user identity: username=%s", username)
                
                # Get fresh collection and wantlist counts using specific endpoints (same as manual refresh)
                if username and username != "Unknown":
                    current_time = time.time()
                    
                    # Check collection update interval
                    collection_interval_minutes = self._endpoint_intervals.get("collection", 10)
                    if collection_interval_minutes > 0:  # Only update if not disabled
                        last_collection_update = self._data["last_updated"].get("collection", 0)
                        collection_interval = collection_interval_minutes * 60  # Convert to seconds
                        
                        if current_time - last_collection_update > collection_interval:
                            collection_count = await self.hass.async_add_executor_job(
                                self.api_client.get_collection_count, username
                            )
                            if collection_count is not None:
                                self._data["collection_count"] = collection_count
                                self._data["last_updated"]["collection"] = current_time
                                _LOGGER.debug("Updated collection count: %s", collection_count)
                    else:
                        _LOGGER.debug("Collection updates disabled (interval = 0)")
                    
                    # Check wantlist update interval
                    wantlist_interval_minutes = self._endpoint_intervals.get("wantlist", 10)
                    if wantlist_interval_minutes > 0:  # Only update if not disabled
                        last_wantlist_update = self._data["last_updated"].get("wantlist", 0)
                        wantlist_interval = wantlist_interval_minutes * 60  # Convert to seconds
                        
                        if current_time - last_wantlist_update > wantlist_interval:
                            wantlist_count = await self.hass.async_add_executor_job(
                                self.api_client.get_wantlist_count, username
                            )
                            if wantlist_count is not None:
                                self._data["wantlist_count"] = wantlist_count
                                self._data["last_updated"]["wantlist"] = current_time
                                _LOGGER.debug("Updated wantlist count: %s", wantlist_count)
                    else:
                        _LOGGER.debug("Wantlist updates disabled (interval = 0)")
                    
                    # Update other endpoints if needed
                    await self._update_endpoints(username)
            else:
                _LOGGER.warning("Failed to get user identity")
            
            self._data["last_updated"]["all"] = time.time()
            
        except Exception as err:
            _LOGGER.error("Error updating Discogs data: %s", err)
        
        return self._data
    
    async def _update_endpoints(self, username: str):
        """Update individual endpoints based on their schedules."""
        current_time = time.time()
        
        # Check collection value (less frequent)
        value_interval_minutes = self._endpoint_intervals.get("collection_value", 30)
        if value_interval_minutes > 0:  # Only update if not disabled
            last_value_update = self._data["last_updated"].get("collection_value", 0)
            value_interval = value_interval_minutes * 60  # Convert to seconds
            
            if current_time - last_value_update > value_interval:
                try:
                    value_data = await self.hass.async_add_executor_job(
                        self.api_client.get_collection_value, username
                    )
                    if value_data:
                        self._data["collection_value"] = value_data
                        self._data["last_updated"]["collection_value"] = current_time
                        _LOGGER.debug("Updated collection value")
                except Exception as err:
                    _LOGGER.debug("Failed to update collection value: %s", err)
        else:
            _LOGGER.debug("Collection value updates disabled (interval = 0)")
        
        # Check random record (even less frequent)
        random_interval_minutes = self._endpoint_intervals.get("random_record", 240)
        if random_interval_minutes > 0:  # Only update if not disabled
            last_random_update = self._data["last_updated"].get("random_record", 0)
            random_interval = random_interval_minutes * 60  # Convert to seconds
            
            if current_time - last_random_update > random_interval:
                try:
                    folder_id = self._data.get("random_record_folder_id", 0)
                    random_data = await self.hass.async_add_executor_job(
                        self.api_client.get_random_record, username, folder_id
                    )
                    if random_data:
                        self._data["random_record"] = random_data
                        self._data["last_updated"]["random_record"] = current_time
                        _LOGGER.debug("Updated random record from folder ID %s", folder_id)
                except Exception as err:
                    _LOGGER.debug("Failed to update random record: %s", err)
        else:
            _LOGGER.debug("Random record updates disabled (interval = 0)")
        
        # Check user lists
        user_lists_interval_minutes = self._endpoint_intervals.get("user_lists", 10)
        if user_lists_interval_minutes > 0:
            last_lists_update = self._data["last_updated"].get("user_lists", 0)
            lists_interval = user_lists_interval_minutes * 60  # Convert to seconds
            
            if current_time - last_lists_update > lists_interval:
                try:
                    lists_data = await self.hass.async_add_executor_job(
                        self.api_client.get_lists, username
                    )
                    if lists_data:
                        self._data["user_lists"] = lists_data
                        self._data["last_updated"]["user_lists"] = current_time
                        _LOGGER.debug("Updated user lists: %s lists", lists_data["count"])
                except Exception as err:
                    _LOGGER.debug("Failed to update user lists: %s", err)
        else:
            _LOGGER.debug("User lists updates disabled (interval = 0)")
        
        # Check user folders
        user_folders_interval_minutes = self._endpoint_intervals.get("user_folders", 10)
        if user_folders_interval_minutes > 0:
            last_folders_update = self._data["last_updated"].get("user_folders", 0)
            folders_interval = user_folders_interval_minutes * 60  # Convert to seconds
            
            if current_time - last_folders_update > folders_interval:
                try:
                    folders_data = await self.hass.async_add_executor_job(
                        self.api_client.get_folders, username
                    )
                    if folders_data:
                        self._data["user_folders"] = folders_data
                        self._data["last_updated"]["user_folders"] = current_time
                        _LOGGER.debug("Updated user folders: %s folders", folders_data["count"])
                except Exception as err:
                    _LOGGER.debug("Failed to update user folders: %s", err)
        else:
            _LOGGER.debug("User folders updates disabled (interval = 0)")
    
    async def manual_refresh_endpoint(self, endpoint: str) -> bool:
        """Manually refresh a specific endpoint."""
        username = self._data.get("user")
        if not username or username == "Unknown":
            return False
        
        try:
            if endpoint == "collection":
                count = await self.hass.async_add_executor_job(
                    self.api_client.get_collection_count, username
                )
                if count is not None:
                    self._data["collection_count"] = count
                    self._data["last_updated"]["collection"] = time.time()
                    self.async_update_listeners()
                    return True
            
            elif endpoint == "wantlist":
                count = await self.hass.async_add_executor_job(
                    self.api_client.get_wantlist_count, username
                )
                if count is not None:
                    self._data["wantlist_count"] = count
                    self._data["last_updated"]["wantlist"] = time.time()
                    self.async_update_listeners()
                    return True
            
            elif endpoint == "collection_value":
                value_data = await self.hass.async_add_executor_job(
                    self.api_client.get_collection_value, username
                )
                if value_data:
                    self._data["collection_value"] = value_data
                    self._data["last_updated"]["collection_value"] = time.time()
                    self.async_update_listeners()
                    return True
            
            elif endpoint == "random_record":
                folder_id = self._data.get("random_record_folder_id", 0)
                random_data = await self.hass.async_add_executor_job(
                    self.api_client.get_random_record, username, folder_id
                )
                if random_data:
                    self._data["random_record"] = random_data
                    self._data["last_updated"]["random_record"] = time.time()
                    self.async_update_listeners()
                    return True
            
            elif endpoint == "user_lists":
                lists_data = await self.hass.async_add_executor_job(
                    self.api_client.get_lists, username
                )
                if lists_data:
                    self._data["user_lists"] = lists_data
                    self._data["last_updated"]["user_lists"] = time.time()
                    self.async_update_listeners()
                    return True
            
            elif endpoint == "user_folders":
                folders_data = await self.hass.async_add_executor_job(
                    self.api_client.get_folders, username
                )
                if folders_data:
                    self._data["user_folders"] = folders_data
                    self._data["last_updated"]["user_folders"] = time.time()
                    self.async_update_listeners()
                    return True
            
        except Exception as err:
            _LOGGER.error("Failed to refresh %s: %s", endpoint, err)
        
        return False
    
    def get_rate_limit_data(self) -> Dict[str, Any]:
        """Get rate limit information."""
        return self.api_client.rate_limit_info
    
    async def get_full_collection(self, folder_id: int = 0) -> list:
        """Get full collection data."""
        username = self._data.get("user")
        if not username or username == "Unknown":
            return []
        
        return await self.hass.async_add_executor_job(
            self.api_client.get_full_collection, username, folder_id
        )
    
    async def get_full_wantlist(self) -> list:
        """Get full wantlist data."""
        username = self._data.get("user")
        if not username or username == "Unknown":
            return []
        
        return await self.hass.async_add_executor_job(
            self.api_client.get_full_wantlist, username
        )
    
    async def get_user_list_items(self, list_id: int) -> list:
        """Get user list items data."""
        username = self._data.get("user")
        if not username or username == "Unknown":
            return []
        
        return await self.hass.async_add_executor_job(
            self.api_client.get_user_list_items, username, list_id
        )