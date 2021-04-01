"""Utility functions."""

import datetime
import pytz
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
        switcher = {
            1: "1",
            2: "2",
            5: "3",
            6: "4",
            7: "5",
            9: "6"
        }
        return "IsOpenZone"+switcher.get(self.pin,"1")

class KI():
    def __init__(self, endpoint):
        self.endpoint = endpoint
        logging.info('endpoint: %s', self.endpoint)
        self.eventlist = []
    
    def has_event(self):
        if len(self.eventlist) > 0:
            return True
        else:
            return False
    
    def set_pin(self, pin, value):
        self.eventlist.append(KIEvent(pin,value))

    def next_event(self):
        if self.has_event():
            return self.eventlist.pop(0)
        else:
            return None
