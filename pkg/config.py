"""Persistent configuration"""
import logging
from gateway_addon import Database


class Config(Database):
    def __init__(self, package_name):
        Database.__init__(self, package_name, None)
        self.endpoint = None
        self.log_level = None
        self.open()
        self.load()

    def load(self):
        try:
            config = self.load_config()
            # config = json.loads(config.decode('utf-8'))
            # logging.info('config %s', config)
            self.endpoint = config['endpoint']
            self.log_level = config['log_level']
            self.devices = None
            self.devices = config['devices']
            self.access = 0
            if 'access' in config
                self.access = config['access']
            # logging.debug(self.devices)
        except Exception as ex:
            logging.exception('Strange config:' + str(ex), config)
