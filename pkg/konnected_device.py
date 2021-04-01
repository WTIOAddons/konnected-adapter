"""Device for DateTime adapter for WebThings Gateway."""

import logging
import threading
import time

from gateway_addon import Device, Event, Action
from .util import KI
from .konnected_property import KITempProperty, KIHumidProperty, \
                                KIAlarmProperty


class KIDevice(Device):
    """Konnected device type."""
    def __init__(self, adapter, _id):
        """
        adapter -- the Adapter for this device
        _id -- ID of this device
        """
        Device.__init__(self, adapter, _id)

    def init(self):
        try:
            self.poll_interval = 2
            self.active_poll = True
            self.thread = threading.Thread(target=self.poll)
            self.thread.daemon = True
            self.thread.start()
        except Exception as ex:
            logging.exception('Exception %s', ex)
        logging.info('KonnectedDevice started')

    def add_property(self, property):
        self.properties[property.name] = property

    def check(self):
        return

    def poll(self):
        """ Poll device for changes."""
        logging.debug('poll START for %s', self.name)
        ixx = 60
        while self.active_poll:
            try:
                time.sleep(self.poll_interval)
                ixx += 1
                if (ixx * self.poll_interval) > 60:  # Every 1 minutes
                    ixx = 0
                self.check()
                for prop in self.properties.values():
                    prop.update()
            except Exception as ex:
                logging.error('THREAD ERR Exception %s', ex)
                logging.exception('Exception %s', ex)
                continue
        logging.debug('POLL STOPPED for device: %s', self.name)


class KonnectedDevice(KIDevice):
    """Konnected device type."""
    def __init__(self, adapter, _id, _config):
        """
        adapter -- the Adapter for this device
        _id -- ID of this device
        """
        KIDevice.__init__(self, adapter, _id)
        self._context = 'https://webthings.io/schemas'
        self._type = ['BinarySensor', 'MultiLevelSensor']
        self.ki = KI(_config.endpoint)

        # logging.info('sunset: %s sunrise: %s', self.sunset, self.sunrise)

        self.add_property(KITempProperty(self, self.ki))
        self.add_property(KIHumidProperty(self, self.ki))
        self.add_property(KIAlarmProperty(self, self.ki))
        self.addZoneEvent('1');
        self.addZoneEvent('2');
        self.addZoneEvent('3');
        self.addZoneEvent('4');
        self.addZoneEvent('5');
        self.addZoneEvent('6');
        self.add_action('alarm',
        {
            'title': 'Alarm',
            'description': 'Sound the siren or silence it',
            'input': {
                'type': 'object',
                'required': [
                    'sound',
                    'duration' # duration is ignored for now
                ],
                'properties': {
                    'sound': {
                        'type': 'boolean'
                    },
                    'duration': {
                        'type': 'integer',
                        'minimum': 1,
                        'unit': 'milliseconds',
                    },
                },
            },
        })
        self.name = 'Konnected'
        self.description = 'Konnected desc'
        self.init()
        logging.debug('Konnected %s', self.as_dict())

    def perform_action(self, action):
        # can do a while here to loop for a bit and then turn it off
        # or can just leave it on until user shuts it off        
        if action.name() == 'alarm':
            logging.debug('Konnected.perform_action: sound the alarm %s',
                          action.input['sound'])
            if action.input['sound'] == True:
                self.set_property('alarm', True)
            else:
                self.set_property('alarm', False)
        # todo: actually sound the alarm or silence it
        return

    def addZoneEvent(self, zone):
        self.add_event('isopenzone'+zone, {
            'title': 'IsOpenZone'+zone, 'label':'IsOpenZone'+zone,
            'description': 'Is Zone '+zone+' opened',
            'type': 'boolean'
        })
        
    def check(self):
        self.check_trigger()

    def check_trigger(self):
        if self.ki.has_event():
            self.check_send_event(self.ki.next_event())


    """ Check if a trigger occured and if so send event """
    def check_send_event(self, event):
        event = Event(self, event.name(), event.state() )
        self.event_notify(event)
        logging.info('New event ' + event_name)
