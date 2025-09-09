"""Simplified sensor platform for Discogs Sync."""
from __future__ import annotations

import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN, 
    ICON_RECORD, ICON_PLAYER, ICON_CASH, ICON_LIST, ICON_FOLDER,
    UNIT_RECORDS, UNIT_LISTS, UNIT_FOLDERS
)

# Sensor definitions with state classes for Google Assistant compatibility
SENSORS = [
    ("collection", "Collection", UNIT_RECORDS, ICON_RECORD, SensorStateClass.MEASUREMENT),
    ("wantlist", "Wantlist", UNIT_RECORDS, ICON_RECORD, SensorStateClass.MEASUREMENT), 
    ("random_record", "Random Record", None, ICON_PLAYER, None),  # No state class for text values
    ("collection_value_min", "Collection Value (Min)", None, ICON_CASH, SensorStateClass.MEASUREMENT),
    ("collection_value_median", "Collection Value (Median)", None, ICON_CASH, SensorStateClass.MEASUREMENT),
    ("collection_value_max", "Collection Value (Max)", None, ICON_CASH, SensorStateClass.MEASUREMENT),
    ("user_lists", "User Lists", UNIT_LISTS, ICON_LIST, SensorStateClass.MEASUREMENT),
    ("user_folders", "User Folders", UNIT_FOLDERS, ICON_FOLDER, SensorStateClass.MEASUREMENT),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DiscogsSensor(coordinator, sensor_key, name, unit, icon, state_class) 
        for sensor_key, name, unit, icon, state_class in SENSORS
    ]
    async_add_entities(entities)


class DiscogsSensor(CoordinatorEntity, SensorEntity):
    """Simplified Discogs sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, sensor_key: str, name: str, unit: str, icon: str, state_class: SensorStateClass = None):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{sensor_key}"
        
        # Set precision for currency values
        if sensor_key.startswith("collection_value_"):
            self._attr_suggested_display_precision = 2
        
        # Don't set entity_category so main sensors can be exposed to Google Assistant
        # Random record is diagnostic since it's not useful for voice queries
        if sensor_key == "random_record":
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.display_name,
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        data = self.coordinator.data
        
        if self._sensor_key == "collection":
            value = data.get("collection_count")
            return value if value is not None else 0
        elif self._sensor_key == "wantlist":
            value = data.get("wantlist_count") 
            return value if value is not None else 0
        elif self._sensor_key == "random_record":
            return data.get("random_record", {}).get("title")
        elif self._sensor_key == "collection_value_min":
            return data.get("collection_value", {}).get("min")
        elif self._sensor_key == "collection_value_median":
            return data.get("collection_value", {}).get("median")
        elif self._sensor_key == "collection_value_max":
            return data.get("collection_value", {}).get("max")
        elif self._sensor_key == "user_lists":
            return data.get("user_lists", {}).get("count", 0)
        elif self._sensor_key == "user_folders":
            return data.get("user_folders", {}).get("count", 0)
        
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Check if we have a username (indicates we've fetched data at least once)
        return self.coordinator.data.get("user") is not None

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        if self._sensor_key.startswith("collection_value_"):
            return self.coordinator.data.get("collection_value", {}).get("currency", "USD")
        return self._attr_native_unit_of_measurement

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        attrs = {"user": self.coordinator.data.get("user")}
        
        # Add specific attributes based on sensor type
        if self._sensor_key == "random_record":
            record_data = self.coordinator.data.get("random_record", {}).get("data", {})
            attrs.update(record_data)
        elif self._sensor_key == "user_lists":
            lists_data = self.coordinator.data.get("user_lists", {}).get("lists", [])
            if lists_data:
                attrs["lists"] = [
                    {
                        list_item.get("id", i): {
                            "id": list_item.get("id"),
                            "name": list_item.get("name"),
                            "uri": list_item.get("uri"),
                            "public": list_item.get("public")
                        }
                    }
                    for i, list_item in enumerate(lists_data)
                ]
        elif self._sensor_key == "user_folders":
            folders_data = self.coordinator.data.get("user_folders", {}).get("folders", [])
            if folders_data:
                attrs["folders"] = [
                    {
                        folder.get("id", i): {
                            "id": folder.get("id"),
                            "count": folder.get("count"),
                            "name": folder.get("name"),
                            "resource_url": folder.get("resource_url")
                        }
                    }
                    for i, folder in enumerate(folders_data)
                ]
        
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
