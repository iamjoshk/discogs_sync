import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN, CONF_NAME
from .const import (
    DOMAIN, DEFAULT_NAME, 
    CONF_ENABLE_SCHEDULED_UPDATES,
    CONF_COLLECTION_UPDATE_INTERVAL, DEFAULT_COLLECTION_UPDATE_INTERVAL,
    CONF_WANTLIST_UPDATE_INTERVAL, DEFAULT_WANTLIST_UPDATE_INTERVAL,
    CONF_COLLECTION_VALUE_UPDATE_INTERVAL, DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL,
    CONF_RANDOM_RECORD_UPDATE_INTERVAL, DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL,
    CONF_USER_LISTS_UPDATE_INTERVAL, DEFAULT_USER_LISTS_UPDATE_INTERVAL,
    CONF_USER_FOLDERS_UPDATE_INTERVAL, DEFAULT_USER_FOLDERS_UPDATE_INTERVAL,
    CONF_API_STATUS_UPDATE_INTERVAL, DEFAULT_API_STATUS_UPDATE_INTERVAL
)

class DiscogsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Discogs."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Optionally: validate token here
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_TOKEN): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_ENABLE_SCHEDULED_UPDATES, default=True): bool,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return DiscogsOptionsFlowHandler(config_entry)


class DiscogsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Discogs options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry
        self._entry_data = config_entry.data
        self._entry_options = config_entry.options
        self._enable_updates = self._entry_options.get(CONF_ENABLE_SCHEDULED_UPDATES, True)

    async def async_step_init(self, user_input=None):
        """First step - determine if updates are enabled."""
        if user_input is not None:
            self._enable_updates = user_input[CONF_ENABLE_SCHEDULED_UPDATES]
            
            if not self._enable_updates:
                # If updates disabled, save simple config
                return self.async_create_entry(
                    title="", 
                    data={CONF_ENABLE_SCHEDULED_UPDATES: False}
                )
            else:
                # If updates enabled, go to intervals step
                return await self.async_step_intervals()

        # Initial form with just enable/disable option
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_ENABLE_SCHEDULED_UPDATES,
                    default=self._enable_updates,
                ): bool,
            }),
            description_placeholders={
                "update_info": "When automatic updates are enabled, you can configure the update intervals for each endpoint."
            },
        )

    async def async_step_intervals(self, user_input=None):
        """Second step - configure intervals if updates are enabled."""
        if user_input is not None:
            # Process the input and preserve existing values if fields are empty/None
            data = {CONF_ENABLE_SCHEDULED_UPDATES: True}
            
            # For each interval, use the user input if provided, otherwise keep existing value
            for key, default in [
                (CONF_COLLECTION_UPDATE_INTERVAL, DEFAULT_COLLECTION_UPDATE_INTERVAL),
                (CONF_WANTLIST_UPDATE_INTERVAL, DEFAULT_WANTLIST_UPDATE_INTERVAL),
                (CONF_COLLECTION_VALUE_UPDATE_INTERVAL, DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL),
                (CONF_RANDOM_RECORD_UPDATE_INTERVAL, DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL),
                (CONF_USER_LISTS_UPDATE_INTERVAL, DEFAULT_USER_LISTS_UPDATE_INTERVAL),
                (CONF_USER_FOLDERS_UPDATE_INTERVAL, DEFAULT_USER_FOLDERS_UPDATE_INTERVAL),
                (CONF_API_STATUS_UPDATE_INTERVAL, DEFAULT_API_STATUS_UPDATE_INTERVAL),
            ]:
                new_value = user_input.get(key)
                if new_value is not None and new_value != "":
                    data[key] = new_value
                else:
                    # Keep existing value or use default
                    data[key] = self._entry_options.get(key, default)
            
            return self.async_create_entry(title="", data=data)

        # Get current values for display
        current_collection = self._entry_options.get(CONF_COLLECTION_UPDATE_INTERVAL, DEFAULT_COLLECTION_UPDATE_INTERVAL)
        current_wantlist = self._entry_options.get(CONF_WANTLIST_UPDATE_INTERVAL, DEFAULT_WANTLIST_UPDATE_INTERVAL)
        current_value = self._entry_options.get(CONF_COLLECTION_VALUE_UPDATE_INTERVAL, DEFAULT_COLLECTION_VALUE_UPDATE_INTERVAL)
        current_random = self._entry_options.get(CONF_RANDOM_RECORD_UPDATE_INTERVAL, DEFAULT_RANDOM_RECORD_UPDATE_INTERVAL)
        current_lists = self._entry_options.get(CONF_USER_LISTS_UPDATE_INTERVAL, DEFAULT_USER_LISTS_UPDATE_INTERVAL)
        current_folders = self._entry_options.get(CONF_USER_FOLDERS_UPDATE_INTERVAL, DEFAULT_USER_FOLDERS_UPDATE_INTERVAL)
        current_api_status = self._entry_options.get(CONF_API_STATUS_UPDATE_INTERVAL, DEFAULT_API_STATUS_UPDATE_INTERVAL)
        
        # Format current intervals display
        def format_interval(interval):
            return "disabled" if interval == 0 else str(interval)
        
        current_intervals = (
            f"Current Update Intervals (in minutes)\n"
            f"Collection: {format_interval(current_collection)}\n"
            f"Wantlist: {format_interval(current_wantlist)}\n"
            f"Collection Value: {format_interval(current_value)}\n"
            f"Random Record: {format_interval(current_random)}\n"
            f"User Lists: {format_interval(current_lists)}\n"
            f"User Folders: {format_interval(current_folders)}\n"
            f"API Status: {format_interval(current_api_status)}"
        )

        # Show interval configuration 
        return self.async_show_form(
            step_id="intervals",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_COLLECTION_UPDATE_INTERVAL,
                    default=current_collection,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_WANTLIST_UPDATE_INTERVAL,
                    default=current_wantlist,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_COLLECTION_VALUE_UPDATE_INTERVAL,
                    default=current_value,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_RANDOM_RECORD_UPDATE_INTERVAL,
                    default=current_random,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_USER_LISTS_UPDATE_INTERVAL,
                    default=current_lists,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_USER_FOLDERS_UPDATE_INTERVAL,
                    default=current_folders,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
                vol.Optional(
                    CONF_API_STATUS_UPDATE_INTERVAL,
                    default=current_api_status,
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
            }),
        )