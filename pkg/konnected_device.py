"""Device for Konnected adapter for WebThings Gateway."""

import logging
import threading
import time
import urllib
import json
from socket import timeout
from gateway_addon import Device, Event
from .util import KI
from .konnected_property import KITempProperty, KIHumidProperty, \
                                KIAlarmProperty, KIDoorProperty, \
                                KIArmedProperty, KIMotionProperty
from .konnected import get_ip_address


class KIDevice(Device):
    """Konnected device type."""
    def __init__(self, adapter, _id):
        """
        adapter -- the Adapter for this device
        _id -- ID of this device
        """
        Device.__init__(self, adapter, _id)
        # self.links.append({
        #    "rel": "alternate",
        #    "mediaType": "text/html",
        #    "href": "/extensions/konnected-adapter?thingId={0}".\
        #        format(urllib.parse.quote(str(_id))),
        # });

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
    def __init__(self, adapter, kdev, _config):
        """
        adapter -- the Adapter for this device
        _id -- ID of this device
        """
        KIDevice.__init__(self, adapter, kdev.sn)
        self._context = 'https://webthings.io/schemas'
        self._type = ['Lock']
        self.ki = KI(_config.endpoint, _config.access)
        self.kurl = kdev.makeUrl("device")
        self.add_property(KIArmedProperty(self, self.ki))
        self.add_property(KIAlarmProperty(self, self.ki))
        sensors = []
        dht = []
        ds18b20 = []
        pinswitch = {
            '1': {'pin': 1},
            '2': {'pin': 2},
            '3': {'pin': 5},
            '4': {'pin': 6},
            '5': {'pin': 7},
            '6': {'pin': 9}
        }
        dhtswitch = {
            '1': {'pin': 1, "poll_interval": 2},
            '2': {'pin': 2, "poll_interval": 2},
            '3': {'pin': 5, "poll_interval": 2},
            '4': {'pin': 6, "poll_interval": 2},
            '5': {'pin': 7, "poll_interval": 2},
            '6': {'pin': 9, "poll_interval": 2}
        }
        # todo use proper device matching serial number, or serial 0
        if (_config.devices):
            logging.debug('got devices')
            logging.debug(_config.devices[0]['zones'])
            for zone in _config.devices[0]['zones']:
                if (zone['sensortype'] == 'door'):
                    sensors.append(pinswitch.get(zone['zone'], None))
                    self.add_property(KIDoorProperty(self, self.ki,
                                                     int(zone['zone']),
                                                     zone['zonename']))
                elif (zone['sensortype'] == 'window'):
                    sensors.append(pinswitch.get(zone['zone'], None))
                    self.add_property(KIDoorProperty(self, self.ki,
                                                     int(zone['zone']),
                                                     zone['zonename']))
                elif (zone['sensortype'] == 'motion'):
                    sensors.append(pinswitch.get(zone['zone'], None))
                    self.add_property(KIMotionProperty(self, self.ki,
                                                       int(zone['zone']),
                                                       zone['zonename']))
                elif (zone['sensortype'] == 'dht'):
                    dht.append(dhtswitch.get(zone['zone'], None))
                    self.add_property(KITempProperty(self, self.ki,
                                                     int(zone['zone']),
                                                     zone['zonename']))
                    self.add_property(KIHumidProperty(self, self.ki,
                                                      int(zone['zone']),
                                                      zone['zonename']))
                elif (zone['sensortype'] == 'ds18b20'):
                    ds18b20.append(dhtswitch.get(zone['zone'], None))
                    self.add_property(KITempProperty(self, self.ki,
                                                     int(zone['zone']),
                                                     zone['zonename']))
        self.add_zone_events()
        self.add_action('toggle', {
            'title': 'Arm/Disarm',
            'description': 'Arm/Disarm',
            '@type': 'ToggleAction',
            'input': {
                'type': 'object',
                'required': [
                    'access'
                ],
                'properties': {
                    'access': {
                        'type': 'integer',
                        'minimum': 0,
                        'maximum': 9999
                    }
                }
            }
        })
        self.add_action('siren', {
            'title': 'Siren',
            'description': 'Sound the siren'
        })
        self.name = 'Konnected-'+str(kdev.sn)
        self.description = 'Konnected device'
        self.init()
        self.provision_dev(_config.endpoint, kdev, sensors, dht, ds18b20)
        logging.debug('Konnected %s', self.as_dict())

    def provision_dev(self, interface, kdev, sensors, dht, ds18b20):
        ip = get_ip_address(interface)
        port = 8001
        actuators = [{"pin": 8, "trigger": 1}]
        kdev.provision(ip, port, sensors, actuators, dht, ds18b20)

    def sound_alarm(self, on):
        logging.debug("sound_alarm")
        payload = {"pin": 8,
                   "state": 1,
                   "momentary": 120000}
        if on is False:
            payload = {"pin": 8,
                       "state": 0}
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        try:
            req = urllib.request.Request(self.kurl,
                                         data=payload.encode('ascii'),
                                         headers=headers,
                                         method='PUT')
            logging.debug("built urllib")
            with urllib.request.urlopen(req, timeout=30) as response:
                the_page = response.read()
            logging.debug(the_page)
        except ConnectionResetError:
            print("==> ConnectionResetError")
            pass
        except timeout:
            print("==> Timeout")
            pass
        logging.debug("Finished setting alarm")
        # response.status should be 200 here todo

    def perform_action(self, action):
        # can do a while here to loop for a bit and then turn it off
        # or can just leave it on until user shuts it off
        logging.debug('perform action')
        logging.debug(action.name)
        if action.name == 'siren':
            logging.debug('Konnected.perform_action: sound the alarm')
            if self.ki.get_alarm():
                self.ki.set_alarm(False)
                self.sound_alarm(False)
            else:
                self.ki.set_alarm(True)
                self.sound_alarm(True)
        if action.name == 'toggle':
            if action.input['access'] == self.ki.get_access():
                logging.debug('Konnected.perform_action: arm or disarm')
                if self.ki.get_armed() == "locked":
                    self.ki.set_armed("unlocked")
                else:
                    self.ki.set_armed("locked")
            else:
                logging.info('Konnected toggle - bad code')
        action.finish()
        return

    def add_zone_events(self):
        self.add_event('zone_open', {
            'title': 'ZoneOpen', 'label': 'ZoneOpen',
            'description': 'Zone opened',
            'type': 'string'
        })
        self.add_event('zone_closed', {
            'title': 'ZoneClosed', 'label': 'ZoneClosed',
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
        wtevent = Event(self, event.name(), event.get_zone())
        self.event_notify(wtevent)
        logging.info('New event ' + event.name())
