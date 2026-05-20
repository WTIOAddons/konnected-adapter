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


# If we haven't heard from the board in this many seconds, assume it
# rebooted (e.g. power loss) and try to re-provision it. The board
# normally pushes sensor state changes whenever they happen, but it
# also sends a periodic heartbeat well under a minute apart, so a
# 5-minute gap is a strong signal something is wrong.
RECONNECT_AFTER_SECONDS = 300

# Don't retry reconnection more often than this. SSDP discovery is
# noisy on the network and provision_dev does a blocking HTTP PUT.
RECONNECT_RETRY_SECONDS = 60


class KIDevice(Device):
    """Konnected device type."""
    def __init__(self, adapter, _id):
        """
        adapter -- the Adapter for this device
        _id -- ID of this device
        """
        Device.__init__(self, adapter, _id)
        # Treat the device as "just heard from" at construction so we
        # don't immediately try to reconnect before it has had a chance
        # to push its first update.
        self.last_seen = time.time()
        self._last_reconnect_attempt = 0.0
        self._is_connected = True
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

    def mark_seen(self):
        """Record that we just heard from the physical device."""
        self.last_seen = time.time()
        if not self._is_connected:
            logging.info('Device %s reachable again', self.name)
            self._is_connected = True
            try:
                self.connected_notify(True)
            except Exception as ex:
                logging.exception('connected_notify(True) failed: %s', ex)

    def maybe_reconnect(self):
        """Hook for subclasses to attempt reconnection. Default no-op."""
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
                # If we haven't heard from the board in a while, try to
                # reconnect. This catches the power-loss case where the
                # board rebooted and forgot its provisioning, so it no
                # longer pushes updates to us.
                if (time.time() - self.last_seen) > RECONNECT_AFTER_SECONDS:
                    self.maybe_reconnect()
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
        # Hold on to the things we'll need to re-provision the board
        # after a power loss: the discovered device handle (for URLBase
        # and the HTTP PUT), and the config (for zone definitions and
        # the network interface name).
        self._kdev = kdev
        self._config = _config
        self.ki = KI(_config.endpoint, _config.access)
        self.kurl = kdev.makeUrl("device")
        self.add_property(KIArmedProperty(self, self.ki))
        self.add_property(KIAlarmProperty(self, self.ki))
        sensors, dht, ds18b20 = self._build_zone_lists(_config, add_properties=True)
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

    def _build_zone_lists(self, _config, add_properties):
        """Build the sensors / dht / ds18b20 lists from the zone config.

        When add_properties is True, also add the WebThings properties
        for each zone. On a re-provision (post-power-loss) we want the
        lists but not duplicate properties, so the adapter can call this
        with add_properties=False.
        """
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
                    if add_properties:
                        self.add_property(KIDoorProperty(self, self.ki,
                                                         int(zone['zone']),
                                                         zone['zonename']))
                elif (zone['sensortype'] == 'window'):
                    sensors.append(pinswitch.get(zone['zone'], None))
                    if add_properties:
                        self.add_property(KIDoorProperty(self, self.ki,
                                                         int(zone['zone']),
                                                         zone['zonename']))
                elif (zone['sensortype'] == 'motion'):
                    sensors.append(pinswitch.get(zone['zone'], None))
                    if add_properties:
                        self.add_property(KIMotionProperty(self, self.ki,
                                                           int(zone['zone']),
                                                           zone['zonename']))
                elif (zone['sensortype'] == 'dht'):
                    dht.append(dhtswitch.get(zone['zone'], None))
                    if add_properties:
                        self.add_property(KITempProperty(self, self.ki,
                                                         int(zone['zone']),
                                                         zone['zonename']))
                        self.add_property(KIHumidProperty(self, self.ki,
                                                          int(zone['zone']),
                                                          zone['zonename']))
                elif (zone['sensortype'] == 'ds18b20'):
                    ds18b20.append(dhtswitch.get(zone['zone'], None))
                    if add_properties:
                        self.add_property(KITempProperty(self, self.ki,
                                                         int(zone['zone']),
                                                         zone['zonename']))
        return sensors, dht, ds18b20

    def provision_dev(self, interface, kdev, sensors, dht, ds18b20):
        ip = get_ip_address(interface)
        port = 8001
        actuators = [{"pin": 8, "trigger": 1}]
        kdev.provision(ip, port, sensors, actuators, dht, ds18b20)

    def maybe_reconnect(self):
        """Try to re-provision the board after a suspected reboot.

        Konnected boards keep no persistent state for endpoint URLs and
        sensor wiring: a power loss wipes everything. The board still
        comes up and rejoins WiFi, but it won't push anything to us
        until it's re-provisioned. We detect this in the poll loop by
        noticing the board has gone quiet (last_seen is stale) and call
        in here to fix it.
        """
        now = time.time()
        if (now - self._last_reconnect_attempt) < RECONNECT_RETRY_SECONDS:
            return
        self._last_reconnect_attempt = now

        # Mark detached so WebThings UI reflects reality while we retry.
        if self._is_connected:
            logging.info('Device %s went quiet; attempting reconnect', self.name)
            self._is_connected = False
            try:
                self.connected_notify(False)
            except Exception as ex:
                logging.exception('connected_notify(False) failed: %s', ex)

        # Re-run SSDP discovery. The board's IP may have changed if
        # DHCP gave it a new lease while it was off, so we can't just
        # reuse the old URLBase.
        try:
            from pkg import konnected as konnected_mod
            devs = konnected_mod.findDevices()
        except Exception as ex:
            logging.exception('findDevices during reconnect failed: %s', ex)
            return

        match = None
        for d in devs:
            if str(d.sn) == str(self.id):
                match = d
                break
        if match is None:
            logging.debug('Device %s not yet visible on SSDP, will retry',
                          self.name)
            return

        # Refresh our handle to the board and re-provision it.
        self._kdev = match
        self.kurl = match.makeUrl("device")
        try:
            sensors, dht, ds18b20 = self._build_zone_lists(self._config,
                                                          add_properties=False)
            self.provision_dev(self._config.endpoint, match,
                               sensors, dht, ds18b20)
        except Exception as ex:
            logging.exception('Re-provisioning %s failed: %s', self.name, ex)
            return

        # provision_dev succeeded — count that as "seen". The next
        # actual push from the board will refresh last_seen again via
        # endpoint.py.
        logging.info('Device %s re-provisioned successfully', self.name)
        self.mark_seen()

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
