"""A simple HTTP server with REST and json for python 3.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import cgi
import json
import threading
import time
from pkg import konnected


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
                data = json.loads(rfile_str)
                serial = int(self.path[len('/api/konnected/device/') + 6:], 16)
                if self.adapter is not None:
                    device = self.adapter.get_device(str(serial))
                    # todo if can't find device yet, see if app will retry
                    if device is not None:
                        if 'state' in data:
                            device.ki.set_pin(data['pin'], data['state'])
                        if 'temp' in data:
                            device.ki.set_temp_pin(data['pin'], data['temp'])
                        if 'humi' in data:
                            device.ki.set_humi_pin(data['pin'], data['humi'])
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
    ip = konnected.get_ip_address(interface)
    port = 8001
    thread = Thread(ip, port, adapter)
    return thread


def main():
    kdevs = konnected.findDevices()
    start_kserver('wlan0', None)
    for kdev in kdevs:
        konnected.provision_dev('wlan0', kdev)
    time.sleep(100000)  # todo: set timeout to 1 day, refresh kdevs


if __name__ == '__main__':
    main()
