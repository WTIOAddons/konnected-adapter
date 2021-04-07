"""Utility functions."""

import logging


class KIEvent():
    def __init__(self, zone, value):
        self.zone = zone
        self.value = value

    def state(self):
        if self.value == 1:
            return True
        else:
            return False

    def get_zone(self):
        return self.zone

    def name(self):
        swState = {
            0: "closed",
            1: "open"
        }
        return "zone_"+swState.get(self.value, "unknown")


class KI():
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.alarm = False
        self.armed = False
        logging.info('endpoint: %s', self.endpoint)
        self.eventlist = []
        self.zones = [None, None, None, None, None, None]
        self.humis = [None, None, None, None, None, None]
        self.switcher = {
            1: 1,
            2: 2,
            5: 3,
            6: 4,
            7: 5,
            9: 6,
        }

    def has_event(self):
        if len(self.eventlist) > 0:
            return True
        else:
            return False

    def get_alarm(self):
        return self.alarm

    def set_alarm(self, alarm):
        self.alarm = alarm

    def get_armed(self):
        return self.armed

    def set_armed(self, armed):
        self.armed = armed

    def get_zone_status(self, zone):
        return self.zones[zone-1]

    def set_zone_status(self, zone, status):
        self.zones[zone-1] = status

    def get_zone_humi(self, zone):
        return self.humis[zone-1]

    def set_zone_humi(self, zone, humid):
        self.humis[zone-1] = humid

    def set_pin(self, pin, value):
        zone = self.switcher.get(pin)
        if zone:
            self.set_zone_status(zone, value)
            self.eventlist.append(KIEvent(zone, value))

    def set_temp_pin(self, pin, value):
        zone = self.switcher.get(pin)
        if zone:
            self.set_zone_status(zone, value)

    def set_humi_pin(self, pin, value):
        zone = self.switcher.get(pin)
        if zone:
            self.set_zone_humi(zone, value)

    def next_event(self):
        if self.has_event():
            return self.eventlist.pop(0)
        else:
            return None
