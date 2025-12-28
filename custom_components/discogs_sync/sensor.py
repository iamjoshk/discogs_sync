"""Simplified sensor platform for Discogs Sync."""
from __future__ import annotations

import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN, 
    ICON_RECORD, ICON_PLAYER, ICON_CASH, ICON_LIST, ICON_FOLDER,
    UNIT_RECORDS, UNIT_LISTS, UNIT_FOLDERS
)

# Simplified sensor definitions
SENSORS = [
    ("collection", "Collection", UNIT_RECORDS, ICON_RECORD),
    ("wantlist", "Wantlist", UNIT_RECORDS, ICON_RECORD), 
    ("random_record", "Random Record", None, ICON_PLAYER),
    ("collection_value_min", "Collection Value (Min)", None, ICON_CASH),
    ("collection_value_median", "Collection Value (Median)", None, ICON_CASH),
    ("collection_value_max", "Collection Value (Max)", None, ICON_CASH),
    ("user_lists", "User Lists", UNIT_LISTS, ICON_LIST),
    ("user_folders", "User Folders", UNIT_FOLDERS, ICON_FOLDER),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DiscogsSensor(coordinator, sensor_key, name, unit, icon) 
        for sensor_key, name, unit, icon in SENSORS
    ]
    async_add_entities(entities)


class DiscogsSensor(CoordinatorEntity, SensorEntity):
    """Simplified Discogs sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, sensor_key: str, name: str, unit: str, icon: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{sensor_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name,
        }

        # Set state class for long-term statistics - ONLY for numeric sensors
        if sensor_key in ["collection", "wantlist", "user_lists", "user_folders"]:
            self._attr_state_class = SensorStateClass.TOTAL
        elif sensor_key.startswith("collection_value_"):
            self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data = self.coordinator.data
        
        if self._sensor_key == "collection":
            value = data.get("collection_count")
            # MUST return numeric value for statistics
            return int(value) if value is not None else 0
        elif self._sensor_key == "wantlist":
            value = data.get("wantlist_count") 
            # MUST return numeric value for statistics
            return int(value) if value is not None else 0
        elif self._sensor_key == "random_record":
            # Text values don't get statistics - no state class
            return data.get("random_record", {}).get("title")
        elif self._sensor_key == "collection_value_min":
            value = data.get("collection_value", {}).get("min")
            # MUST return numeric value for statistics, can't be None
            return float(value) if value is not None else 0.0
        elif self._sensor_key == "collection_value_median":
            value = data.get("collection_value", {}).get("median")
            # MUST return numeric value for statistics, can't be None
            return float(value) if value is not None else 0.0
        elif self._sensor_key == "collection_value_max":
            value = data.get("collection_value", {}).get("max")
            # MUST return numeric value for statistics, can't be None
            return float(value) if value is not None else 0.0
        elif self._sensor_key == "user_lists":
            value = data.get("user_lists", {}).get("count", 0)
            # MUST return numeric value for statistics
            return int(value)
        elif self._sensor_key == "user_folders":
            value = data.get("user_folders", {}).get("count", 0)
            # MUST return numeric value for statistics
            return int(value)
        
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity must be available for statistics to work
        return self.coordinator.data.get("user") is not None

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        if self._sensor_key.startswith("collection_value_"):
            currency = self.coordinator.data.get("collection_value", {}).get("currency", "USD")
            # Ensure consistent currency format for statistics
            return currency.upper() if currency else "USD"
        return self._attr_native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {"user": self.coordinator.data.get("user")}
        
        # Add specific attributes based on sensor type
        if self._sensor_key == "random_record":
            record_data = self.coordinator.data.get("random_record", {}).get("data", {})
            attrs.update(record_data)
            # Add release_id for image download service
            if "basic_information" in record_data:
                attrs["release_id"] = record_data["basic_information"].get("id")
        elif self._sensor_key == "user_lists":
            lists_data = self.coordinator.data.get("user_lists", {}).get("lists", [])
            if lists_data:
                attrs["lists"] = []
                for list_item in lists_data:
                    list_name = list_item.get("name", "Unknown List")
                    attrs["lists"].append({
                        list_name: {
                            "id": list_item.get("id"),
                            "uri": list_item.get("uri"),
                            "public": list_item.get("public")
                        }
                    })
        elif self._sensor_key == "user_folders":
            folders_data = self.coordinator.data.get("user_folders", {}).get("folders", [])
            if folders_data:
                attrs["folders"] = []
                for folder in folders_data:
                    folder_name = folder.get("name", "Unknown Folder")
                    attrs["folders"].append({
                        folder_name: {
                            "id": folder.get("id"),
                            "count": folder.get("count"),
                            "name": folder.get("name"),
                            "resource_url": folder.get("resource_url")
                        }
                    })
        
        # Add last updated timestamp
        last_updated_key = self._get_last_updated_key()
        if last_updated_key:
            timestamp = self.coordinator.data.get("last_updated", {}).get(last_updated_key)
            if timestamp:
                attrs["last_updated"] = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        return attrs
    
    def _get_last_updated_key(self) -> Optional[str]:
        """Get the last updated key for this sensor type."""
        mapping = {
            "collection": "collection",
            "wantlist": "wantlist", 
            "random_record": "random_record",
            "collection_value_min": "collection_value",
            "collection_value_median": "collection_value", 
            "collection_value_max": "collection_value",
            "user_lists": "user_lists",
            "user_folders": "user_folders",
        }
        return mapping.get(self._sensor_key)