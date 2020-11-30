[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

*Please :star: this repo if you find it useful*

<p align="left"><br>
<a href="https://paypal.me/eyalco1967?locale.x=he_IL" target="_blank"><img src="http://khrolenok.ru/support_paypal.png" alt="PayPal" width="250" height="48"></a>
</p>

# Kan Program

A custom component to get current and next Israel Kan program.

### MANUAL INSTALLATION

1. Download the `kan_program.zip` file from the
   [latest release](https://github.com/eyalcha/kan_program/releases/latest).
2. Unpack the release and copy the `custom_components/kan_program` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure Kan stations (radio / tv) you want to track.
4. Restart Home Assistant.

### INSTALLATION VIA HACS

1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the `kan_program` integration.
3. Configure the `kan_program` integration.
4. Restart Home Assistant.

## Configuration

Define the stations to be tracked in `configuration.yaml`

Example:

```yaml
sensor:
  - platform: kan_program
    station_id: 9
```

The above configuration will generate an entity with the id `kan_program.kan_gimel` and current program as the state along with these attributes:

```
attribution: Data provided by kan.org.il
station_name: Kan Gimel
description: ...
start_time: ...
end_time: ...
chapter_number: ...
next: ...
friendly_name: Kan Gimel
icon: 'mdi:radio'
```

# Services

The component also exposes the service kan_prohgram.refresh which will refresh all the data.

# Kan Stations id's

Id | Station
---|---
1  | Kan 11
2  | Makan
3  |
4  | Kan 88
5  | Kan Tarbut
6  | Kan Reka
8  | Kan Moreshet
7  | Kan Kol Hamusika
8  | Kan Bet
9  | Kan Gimel
10 | Kan
