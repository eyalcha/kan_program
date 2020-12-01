"""
A component which shows the current and next radio station program
https://github.com/eyalcha/radioprogram
"""

import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_CHAPTER_NUMBER,
    ATTR_DESCRIPTION,
    ATTR_END_TIME,
    ATTR_NEXT,
    ATTR_START_TIME,
    ATTR_STATION_NAME,
    ATTRIBUTION,
    BASE_URL_GUIDE,
    CONF_STATION_ID,
    DEFAULT_ICON,
    DOMAIN,
    STATION_NAME,
    SERVICE_REFRESH,
)

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_FORMAT = DOMAIN + ".{}"
SCAN_INTERVAL = timedelta(minutes=15)
DEFAULT_TIMEOUT = 10

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STATION_ID): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
    }
)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Set up the Radio Program sensor."""
    station_id = config.get(CONF_STATION_ID, [])
    name = config.get(CONF_NAME, STATION_NAME[str(station_id)])

    coordinator = KanProgramUpdateCoordinator(
        station_id, hass, config.get(CONF_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    sensors = []
    sensors.append(KanProgramSensor(hass, coordinator, name, station_id))

    # The True param fetches data first time before being written to HA
    async_add_entities(sensors, True)

    async def handle_refresh(_call):
        """Refresh data."""
        _LOGGER.info("Processing refresh")
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        handle_refresh,
    )

    _LOGGER.debug("Refresh service registered")


class KanProgramSensor(Entity):
    """Defines a Yahoo finance sensor."""

    # pylint: disable=too-many-instance-attributes
    _icon = DEFAULT_ICON
    _station_id = None
    _name = None
    _state = None
    _attributes = {}

    def __init__(self, hass, coordinator, name, station_id) -> None:
        """Initialize the sensor."""
        self._name = name
        self._station_id = station_id
        self._coordinator = coordinator
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, name.lower().replace(" ", "_"), hass=hass
        )
        _LOGGER.debug("Created %s", self.entity_id)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def fetch_data(self) -> None:
        """Fetch data and populate local fields."""
        programs = self._coordinator.data
        if programs is None:
            return
        # Search for current / next program
        current_program = None
        next_program = None
        for p in programs:
            time_start = datetime.strptime(p["start_time"], "%Y-%m-%dT%H:%M:%S")
            time_end = datetime.strptime(p["end_time"], "%Y-%m-%dT%H:%M:%S")
            if time_start <= datetime.now() < time_end:
                current_program = p
            if time_start > datetime.now() and next_program is None:
                next_program = p
        # Set sensor state
        if current_program:
            self._state = current_program["title"]
        # Set attributes
        self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
        self._attributes[ATTR_STATION_NAME] = STATION_NAME[str(self._station_id)]
        if current_program:
            self._attributes[ATTR_DESCRIPTION] = current_program["live_desc"]
            self._attributes[ATTR_START_TIME] = current_program["start_time"]
            self._attributes[ATTR_END_TIME] = current_program["end_time"]
            self._attributes[ATTR_CHAPTER_NUMBER] = current_program["chapter_number"]
        if next_program:
            self._attributes[ATTR_NEXT] = next_program["title"]
        _LOGGER.debug(current_program)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        self.fetch_data()
        return self._coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        self._coordinator.async_remove_listener(self.async_write_ha_state)

    async def async_update(self) -> None:
        """Update symbol data."""
        await self._coordinator.async_request_refresh()


class KanProgramUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage Yahoo finance data update."""

    def __init__(self, station_id, hass, update_interval) -> None:
        """Initialize."""
        self._station_id = station_id
        self._data = None
        self.loop = hass.loop
        self.websession = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch the latest data from the source."""
        try:
            await self.update()
        except () as error:
            raise UpdateFailed(error)
        return self._data

    async def get_json(self):
        """Get the JSON data."""
        json = None
        try:
            url = "{}?stationID={}&day={}".format(
                BASE_URL_GUIDE, self._station_id, datetime.today().strftime("%d/%m/%Y")
            )
            _LOGGER.debug("Url = %s", url)
            async with async_timeout.timeout(DEFAULT_TIMEOUT, loop=self.loop):
                response = await self.websession.get(url)
                json = await response.json(content_type="text/html")

            # _LOGGER.debug("Data = %s", json)
            self.last_update_success = True
        except asyncio.TimeoutError:
            _LOGGER.error("Timed out getting data")
            self.last_update_success = False
        except aiohttp.ClientError as exception:
            _LOGGER.error("Error getting data: %s", exception)
            self.last_update_success = False

        return json

    async def update(self):
        """Update data."""
        json = await self.get_json()
        if json is not None:
            if "error" in json:
                raise ValueError(json["error"]["info"])

        self._data = json
        _LOGGER.debug("Data updated")
