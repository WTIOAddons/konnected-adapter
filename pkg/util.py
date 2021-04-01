"""Utility functions."""

import logging
import math

class KIEvent():
    def __init__(self, pin, value):
        self.pin = pin
        self.value = value

    def state(self):
        if self.value == '1':
            return True
        else:
            return False

    def name(self):
        swState = {
            '0': "Closed",
            '1': "Open"
        }
        return "Zone"+swState.get(self.value,"Closed")

class KI():
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.alarm = False
        logging.info('endpoint: %s', self.endpoint)
        self.eventlist = []
        self.zones = [None, None, None, None, None, None]
    
    def has_event(self):
        if len(self.eventlist) > 0:
            return True
        else:
            return False

    def get_temperature(self):
        return 0

    def get_humidity(self):
        return 0

    def get_alarm(self):
        return self.alarm

    def set_alarm(self, alarm):
        self.alarm = alarm

    def get_zone_status(self, zone):
        return self.zones[zone-1]

    def set_zone_status(self, zone, status):
        self.zones[zone-1] = status
        
    def set_pin(self, pin, value):
        switcher = {
            1: 1,
            2: 2,
            5: 3,
            6: 4,
            7: 5,
            9: 6,
        }
        self.set_zone_status(switcher.get(pin,1), value)
        self.eventlist.append(KIEvent(pin,value))

    def next_event(self):
        if self.has_event():
            return self.eventlist.pop(0)
        else:
            return None
