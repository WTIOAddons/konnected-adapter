"""Adapter for DateTime adapter for WebThings Gateway."""

import logging
import time
from gateway_addon import Adapter
from .config import Config
from .konnected_device import KonnectedDevice
from pkg import konnected
from pkg import endpoint
from .konnected_api import KonnectedAPI


class KonnectedAdapter(Adapter):
    """Konnected Adapter to support Konnected.io alarm board."""

    def __init__(self, verbose=False):
        """
        verbose -- enable verbose logging
        """
#        logging.getLogger().setLevel(logging.DEBUG)
        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'konnected-adapter',
                         'konnected-adapter',
                         verbose=verbose)
        self._config = Config(self.package_name)
        self.api_handler = KonnectedAPI(self, verbose=verbose)
        endpoint.start_kserver(self._config.endpoint, self)
        self.start_pairing(1)

    def start_pairing(self, timeout):
        """  Start pairing process. """
        logging.debug('START Pairing')

        log_level = 10
        if self._config.log_level == 'INFO':
            logging.getLogger().setLevel(logging.INFO)
        elif self._config.log_level == 'DEBUG':
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.WARNING)
        logging.info("Log level %s", log_level)

        devs = konnected.findDevices()
        self.kdevs = devs
        for dev in devs:
            if self.get_device(dev.sn) is None:
                logging.debug('adding device %s', str(dev.sn))
                self.handle_device_added(KonnectedDevice(self, dev,
                                                         self._config))
            else:
                logging.debug('Device: %s was already created', dev.sn)
        logging.debug('END Pairing')

    def cancel_pairing(self):
        """Cancel pairing process."""
        logging.debug('cancel_pairing')

    def unload(self):
        """Perform any necessary cleanup before adapter is shut down."""
        logging.debug('Start unload all devices')
        try:
            for device_id, device in self.get_devices().items():
                device.active_poll = False
            time.sleep(3)
            for dev_id, dev in self.get_devices().items():
                logging.debug('UNLOAD Device: %s', dev_id)
                super().unload()
        except Exception as ex:
            logging.exception('Exception %s', ex)
        logging.debug('End unload all devices')

    def handle_device_removed(self, device):
        logging.debug('Device to be removed name: %s is_alive: %s',
                      device.name, device.thread.is_alive())
        device.active_poll = False
        device.thread.join(20.0)
        logging.debug('Device id: %s is_alive: %s', device.id,
                      device.thread.is_alive())
        super().handle_device_removed(device)
        logging.debug('device:' + device.name + ' is removed. Device ' +
                      device.id)
