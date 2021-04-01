# Konnected adapter

Konnected.io adapter for WebThings Gateway.

Purpose: Create adapter to Konnected.io devices which replace alarms

## Upgrade ##
After upgrade the addon the pages must be reloaded before the new attributes are visible.  

## Release notes ##

0.0.1
 * Initial release.

## Konnected things have the following properties and events
 * IsOpenZone1...IsOpenZone12 (a boolean event, zones 1-12)
 * Temp (property)
 * Humidity (property)

## Configuration
Configure the log level and the interface (wireless or wired end point name)

## Example
Turn the lamp in bedroom only on weekdays
`if the time of day is 06:13 and DateTime is not weekend, turn BedroomLamp on

To start the fan evey hour and switch it of after 5 minutes  
`if DateTime minute is 20, turn Fan on`  
`if DateTime minute is 25, turn Fan off`

To start the fan evey second hour when it is dark and switch it of after 5 minutes  
`if DateTime is dark and DateTime minute is 20 and DateTime is even_hour, turn Fan on`  
`if DateTime minute is 25, turn Fan off`

If its only for 5 minutes
`while DateTime minutes5 is 5, turn Fan on`

A motion sensor is only active between 10:00--10:59 
`if DateTime Hour is greater than 9 and DateTime Hour is less than 11 and Motion sensor is motion, turn Light on`

Open blinds 15 minutes before sunrise (configure -15 for offset mins)
`if DateTime event "Sunrise offset -15 mins" occurs, do Scene Controller action "AllOpen"`

Close blinds because the sun hits your eye like a big pizza pie (look at controller for az/el parameters when blinded)
`if DateTime Azimuth is greater than -112, DateTime Azimuth is less than -95, DateTime Elevation is less than 7, DateTime Elevation is greater than 2, set Blind-1 Level to 50`

## Bugs


```
sudo apt install python3-dev
sudo pip3 install git+https://github.com/WebThingsIO/gateway-addon-python.git
```
