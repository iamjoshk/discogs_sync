"""Select platform for Discogs Sync."""
from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, ICON_FOLDER


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Discogs select entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        DiscogsRandomRecordFolderSelect(coordinator)
    ]
    
    async_add_entities(entities)


class DiscogsRandomRecordFolderSelect(CoordinatorEntity, SelectEntity):
    """Select entity for choosing which folder to use for random records."""
    
    _attr_has_entity_name = True
    _attr_icon = ICON_FOLDER
    _attr_entity_category = EntityCategory.CONFIG
    
    def __init__(self, coordinator):
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_name = "Random Record Folder"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_random_record_folder"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name
        }
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.data.get("user") is not None
    
    @property
    def options(self) -> list[str]:
        """Return list of available folder options."""
        folders_data = self.coordinator.data.get("user_folders", {}).get("folders", [])
        if not folders_data:
            return ["All"]  # Default fallback
        
        folder_names = []
        for folder in folders_data:
            folder_name = folder.get("name", "Unknown Folder")
            folder_names.append(folder_name)
        
        return folder_names
    
    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        # Get the stored selection from coordinator data, default to "All"
        return self.coordinator.data.get("random_record_folder_selection", "All")
    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Store the selection in coordinator data
        self.coordinator.data["random_record_folder_selection"] = option
        
        # Find the folder ID for the selected name
        folders_data = self.coordinator.data.get("user_folders", {}).get("folders", [])
        selected_folder_id = 0  # Default to "All" folder
        
        for folder in folders_data:
            if folder.get("name") == option:
                selected_folder_id = folder.get("id", 0)
                break
        
        # Store the folder ID as well
        self.coordinator.data["random_record_folder_id"] = selected_folder_id
        
        # Persist the selection to config entry data for restoration after restart
        new_data = dict(self.coordinator.config_entry.data)
        new_data["random_record_folder_selection"] = option
        new_data["random_record_folder_id"] = selected_folder_id
        
        self.hass.config_entries.async_update_entry(
            self.coordinator.config_entry, 
            data=new_data
        )
        
        # Trigger an update of listeners
        self.coordinator.async_update_listeners()
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attrs = {
            "user": self.coordinator.data.get("user"),
            "selected_folder_id": self.coordinator.data.get("random_record_folder_id", 0)
        }
        return attrs
