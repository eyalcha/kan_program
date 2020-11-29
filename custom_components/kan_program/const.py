"""Constants for Kan Program guide sensor."""

DEFAULT_ICON = "mdi:radio"
DOMAIN = "kan_program"

BASE_URL_GUIDE = "https://www.kan.org.il/tv-guide/tv_guidePrograms.ashx"
BASE_URL_PICTURES = "https://kanweb.blob.core.windows.net/download/pictures"

# Sensor configuration
CONF_STATION_ID = "station_id"

# Sensor attributes
ATTR_NEXT = "next"
ATTR_STATION_NAME = "station_name"
ATTR_DESCRIPTION = "description"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"
ATTR_CHAPTER_NUMBER = "chapter_number"

ATTRIBUTION = "Data provided by kan.org.il"

# Station name
STATION_NAME = {
  "1": "Kan 11",
  "2": "Makan",
  "3": "Kan ?",
  "4": "Kan 88",
  "5": "Kan Tarbut",
  "6": "Kan Reka",
  "8": "Kan Moreshet",
  "7": "Kan Kol Hamusika",
  "8": "Kan Bet",
  "9": "Kan Gimel",
  "10": "Kan ?",
}


