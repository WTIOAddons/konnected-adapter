# Konnected adapter

Konnected.io adapter for WebThings Gateway.

Purpose: Create adapter to Konnected.io devices which replace alarms

## Upgrade ##
After upgrade the addon the pages must be reloaded before the new attributes are visible.  

## Release notes ##

0.2.0
 * Build matrix now produces working artifacts across all platform/Python combinations again after a long sequence of toolchain fixes
 * Power-loss reconnection from 0.1.2 onward is the user-facing improvement that started this release cycle

0.1.9
 * Pinned jsonschema below 4.18 for Python 3.7/3.8 builds so the dep chain stays on pure-Python pyrsistent and avoids the Rust-backed rpds-py that has no cp38 armv7 wheel

0.1.8
 * Tightened the cryptography pin to <46 so linux-arm 3.7/3.8 builds use the dual-tagged manylinux_2_28 armv7 wheel and don't fall back to a Rust source build

0.1.7
 * Pinned cryptography below version 48 for Python 3.7/3.8 builds (cryptography 48 dropped cp38 wheels for armv7, breaking linux-arm builds)

0.1.6
 * Pinned Python 3.7 build matrix entries to older runners (ubuntu-22.04, macos-13) since newer runner images no longer ship Python 3.7

0.1.5
 * Use prebuilt wheels for Python 3.7 and 3.8 builds, source builds for 3.9+

0.1.4
 * Fixed Linux cross-compile build by removing the obsolete `qemu` apt metapackage

0.1.3
 * Modernized GitHub Actions release workflow (older action versions had been deprecated)

0.1.2
 * Reconnect automatically after the Konnected board reboots (e.g. power loss)
 * Previously the device would stay detached in WebThings.io until removed and re-added

0.1.1
 * Made Armed property into an enum to make it easier to use in rules
 * In 0.1.0 you had to type in "locked" or "unlocked" into the rule

0.1.0
 * Initial release for version that has access codes built in
 * During config, enter the access code you will use
 * On the Thing you create, that code is required to lock or unlock

0.0.4
 * Major bug in 0.0.3 with zone_closed event, fixed in 0.0.4

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
