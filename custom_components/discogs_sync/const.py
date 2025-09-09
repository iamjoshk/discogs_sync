"""Constants for the Discogs Sync integration."""

DOMAIN = "discogs_sync"
DEFAULT_NAME = "Discogs Sync"

# Define a specific user agent for Discogs API
USER_AGENT = "DiscogsSync/1.0 +https://github.com/iamjoshk/discogs_sync"

# Configuration options
CONF_ENABLE_SCHEDULED_UPDATES = "enable_scheduled_updates"
CONF_COLLECTION_UPDATE_INTERVAL = "collection_update_interval"
CONF_WANTLIST_UPDATE_INTERVAL = "wantlist_update_interval"
CONF_COLLECTION_VALUE_UPDATE_INTERVAL = "collection_value_update_interval"
CONF_RANDOM_RECORD_UPDATE_INTERVAL = "random_record_update_interval"

# Default values (in minutes)
DEFAULT_COLLECTION_UPDATE_INTERVAL = 10
DEFAULT_WANTLIST_UPDATE_INTERVAL = 10
DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL = 30
DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL = 240

# Attributes
UNIT_RECORDS = "releases"
UNIT_LISTS = "lists"
UNIT_FOLDERS = "folders"
ICON_RECORD = "mdi:album"
ICON_PLAYER = "mdi:record-player"
ICON_CASH = "mdi:cash"
ICON_LIST = "mdi:format-list-bulleted"
ICON_FOLDER = "mdi:folder-multiple"
