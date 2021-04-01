"""A simple HTTP server with REST and json for python 3.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import konnected
import re
import cgi
import json
import threading
import socket
import fcntl
import struct
import time
from konnected_adapter import KonnectedAdapter
from urllib import parse

z1 = 1
z2 = 2
z3 = 5
z4 = 6
z5 = 7
z6 = 9
zout = 8


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, adapter):
        self.adapter = adapter

    def __call__(self, *args, **kwargs):
        """ Handle a request """
        super().__init__(*args, **kwargs)

    def do_PUT(self):
        print(self.path)
        if re.search('/api/konnected/*', self.path):
            ctype, pdict = cgi.parse_header(
                self.headers.get('content-type'))
            if ctype == 'application/json':
                length = int(self.headers.get('content-length'))
                rfile_str = self.rfile.read(length).decode('utf8')
                print("rfile")
                print(rfile_str)
                data = json.loads(rfile_str)
                print("\ndata")
                print(data)
                print("\npin")
                print(data['pin'])
                print("\nstate")
                print(data['state'])
                if self.adapter is not None:
                    device=self.adapter.get_device('14290783')
                    device.ki.set_pin(data['pin'], data['state'])
                self.send_response(200)
            else:
                # HTTP 400: bad request
                self.send_response(400, "Bad Request: must give data")
        else:
            # HTTP 403: forbidden
            self.send_response(403)
        self.end_headers()

    def do_GET(self):
        if re.search('/api/konnected/shutdown', self.path):
            # Must shutdown in another thread or we'll hang
            def kill_me_please():
                self.server.shutdown()
            threading.Thread(target=kill_me_please).start()

            # Send out a 200 before we go
            self.send_response(200)
        else:
            self.send_response(403)

        self.end_headers()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf8'))
    )[20:24])

class Thread(threading.Thread):
    def __init__(self, ip, port, adapter):
        threading.Thread.__init__(self)
        handler = HTTPRequestHandler(adapter)
        self.server = HTTPServer((ip, port), handler)
        self.daemon = True
        self.start()

    def run(self):
        print('HTTP Server Running...........')
        self.server.serve_forever()


def start_kserver(interface, adapter):
    ip = get_ip_address(interface)
    port = 8001
    thread = Thread(ip, port, adapter)

def provision_dev(interface, kdev):
    ip = get_ip_address(interface)
    port = 8001
    sensors = [{"pin":1},{"pin":2},{"pin":5},
               {"pin":6},{"pin":7},{"pin":9}]
    actuators = [{"pin":8,"trigger":1}]
    dht_sensors=[] # [{"pin":9,"poll_interval":2}]
    ds18b20_sensors=[]
    logging.info('kdev: %s', kdev)
    kdev.provision(ip, port, sensors, actuators, dht_sensors,
                   ds18b20_sensors)

def main():
    kdevs = konnected.findDevices()
    start_kserver('wlan0', None)
    for kdev in kdevs:
        provision_dev('wlan0', kdev)
    time.sleep(100000) # todo: set timeout to 1 day, refresh kdevs

if __name__ == '__main__':
    main()
