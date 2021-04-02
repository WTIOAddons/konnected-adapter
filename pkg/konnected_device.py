"""Device for DateTime adapter for WebThings Gateway."""

import logging
import threading
import time
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from gateway_addon import Device, Event, Action
from .util import KI
from .konnected_property import KITempProperty, KIHumidProperty, \
                                KIAlarmProperty, KIDoorProperty, \
                                KIArmedProperty


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

    def request_action(self, action_id, action_name, action_input):
        """
        Request that a new action be performed.
        action_id -- ID of the new action
        action_name -- name of the action
        action_input -- any inputs to the action
        """
        logging.debug('request action '+action_name)
        if action_name not in self.actions:
            return
        logging.debug('action in')

        # Validate action input, if present.
        metadata = self.actions[action_name]
        if 'input' in metadata:
            try:
                validate(action_input, metadata['input'])
            except ValidationError:
                return
        logging.debug('action valid')
        action = Action(action_id, self, action_name, action_input)
        logging.debug('action going')
        self.perform_action(action)
        logging.debug('action performed')


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
        self._type = ['OnOffSwitch','Alarm' 
                      'DoorSensor']
        self.ki = KI(_config.endpoint)

        # logging.info('sunset: %s sunrise: %s', self.sunset, self.sunrise)

        self.add_property(KIArmedProperty(self, self.ki))
        self.add_property(KITempProperty(self, self.ki))
        self.add_property(KIHumidProperty(self, self.ki))
        self.add_property(KIAlarmProperty(self, self.ki))
        for zone in range(1,6): # 1-5 zones
            self.add_property(KIDoorProperty(self, self.ki, zone))
        self.add_zone_events();
        self.add_action('siren',
        {
            'title': 'Siren',
            'description': 'Sound the siren',
            'type': 'string',
            '@type':'AlarmEvent'
        })
        self.add_action('provision', {
            'title': 'Provision',
            'description': 'Provision the zones',
            'input': {
                'type': 'object',
                'required': [
                    'zonename',
                    'sensortype',
                    'pin'
                ],
                'properties': {
                    'zonename': {
                        'type': 'string'
                    },
                    'sensortype': {
                        'type': 'string',
                        'enum': [
                            'door',
                            'motion',
                            'dht',
                            'ds18b20'
                        ]
                    },
                    'zone': {
                        'type': 'integer',
                        'enum': [
                            1,2,3,4,5,6
                        ]
                    }
                },
            },
        })
        self.name = 'Konnected-'+str(_id)
        self.description = 'Konnected device'
        self.init()
        logging.debug('Konnected %s', self.as_dict())

    def perform_action(self, action):
        # can do a while here to loop for a bit and then turn it off
        # or can just leave it on until user shuts it off      
        logging.debug('perform action')
        logging.debug(action.name)  
        if action.name == 'siren':
            logging.debug('Konnected.perform_action: sound the alarm %s')
            if self.ki.get_alarm():
                self.set_property('alarm', False)
                self.ki.set_alarm(False)
            else:
                self.set_property('alarm', True)
                self.ki.set_alarm(True)
        elif action.name == 'provision':
            logging.debug('Performing provision')
            if action.input['type'] == 'door' or action.input['type'] == 'motion':
                self.add_property(KIDoorProperty(self, self.ki, 
                                                 action.input['zone']))
        action.finish()
        # todo: actually sound the alarm or silence it
        return

    def add_zone_events(self):
        self.add_event('zone_open', {
            'title': 'ZoneOpen', 'label':'ZoneOpen',
            'description': 'Zone opened',
            'type': 'string'
        })
        self.add_event('zone_closed', {
            'title': 'ZoneClosed', 'label':'ZoneClosed',
            'description': 'Zone closed',
            'type': 'string'
        })

    def check(self):
        self.check_trigger()

    def check_trigger(self):
        if self.ki.has_event():
            self.check_send_event(self.ki.next_event())


    """ Check if a trigger occured and if so send event """
    def check_send_event(self, event):
        wtevent = Event(self, event.name(), event.get_zone() )
        self.event_notify(wtevent)
        logging.info('New event ' + event.name())
