# Konnected adapter

Konnected.io adapter for WebThings Gateway.

Purpose: Create adapter to Konnected.io devices which replace alarms

## Upgrade ##
After upgrade the addon the pages must be reloaded before the new attributes are visible.  

## Release notes ##

0.0.4
 * Use this release; major bug in 0.0.3 with zone_closed event

0.0.3
 * Initial release.

## Konnected things have the following properties and events
 * Armed (a boolean property, set by the toggle action)
 * Siren (alarm property) set when alarm is triggered
 * zone_open (Event triggered when door or motion occurs)
 * zone_closed (Event triggered when door or motion occurs)
 * Optional properties depend on configuration
 * Temperature (optional number property)
 * Humidity (optional integer property)
 * Door (optional door or window property, open or closed)
 * Motion (optional motion property, motion or no motion)


## Configuration
Configure the log level and the interface (wireless or wired end point name)

## Example
Turn on the lamp in bedroom when motion occurs after dark in the family room
`if Konnected-xxxxx is Family Room Motion and DateTime is Dark, turn BedroomLamp on`

Sound alarm when zone is breached
`if Kon-xxxx event "ZoneOpen" occurs, and Kon-xxx is Armed do Kon-xxxx action "Siren"`

## Bugs


```
sudo apt install python3-dev
sudo pip3 install git+https://github.com/WebThingsIO/gateway-addon-python.git
```
