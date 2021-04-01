#   Copyright 2021 Bill Fahle
#
#   Licensed under the Mozilla License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       https://mozilla.org/en-US/MPL/2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import xml.etree.ElementTree as ET
import urllib.request
import json
import socket
import fcntl
import struct
import logging

from pkg import ssdp

NS = '{urn:schemas-upnp-org:device-1-0}'
# XPATH TO FIND MVERSION
xPathmaj = ''.join([
    "./",
    NS, "specVersion/",
    NS, "major"
    ])

# XPATH TO FIND mVERSION
xPathmin = ''.join([
    "./",
    NS, "specVersion/",
    NS, "minor"
    ])

# XPATH TO FIND URLBase
xPathURLb = ''.join([
    "./",
    NS, "URLBase"
    ])

# XPATH TO FIND UUID
xPathUDN = ''.join([
    "./",
    NS, "device/",
    NS, "UDN"
    ])

# XPATH TO FIND modelNumber
xPathMN = ''.join([
    "./",
    NS, "device/",
    NS, "modelNumber"
    ])

# XPATH TO FIND serialNumber
xPathSN = ''.join([
    "./",
    NS, "device/",
    NS, "serialNumber"
    ])

class konnected_dev:
    def __init__(self,device):
        response = urllib.request.urlopen(device.location).read()
        tree = ET.fromstring(response)
        for udn in tree.findall(xPathUDN):
            self.udn = udn.text
        for mdn in tree.findall(xPathMN):
            self.mn = mdn.text
        for sn in tree.findall(xPathSN):
            self.sn = sn.text
        for urlb in tree.findall(xPathURLb):
            self.URLBase = urlb.text
        for maj in tree.findall(xPathmaj):
            majt = maj.text
        for mn in tree.findall(xPathmin):
            mint = mn.text
        self.version = majt+"."+mint;

    def makeUrl(self, rest):
        return self.URLBase+"/"+rest
    
    def provision(self, ip, port, sensors, actuators, dht_sensors,
                  ds18b20_sensors):
        payload={"endpoint_type":"rest",
                            "endpoint":"http://"+ip+":"+str(port)+
                                       "/api/konnected",
                            "token":"WebThings",
                            "sensors":sensors,
                            "actuators":actuators,
                            "dht_sensors":dht_sensors,
                            "ds18b20_sensors":ds18b20_sensors}
        # print(payload)
        # print(self.makeUrl("settings"))
        payload=json.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        try:
            req = urllib.request.Request(self.makeUrl("settings"),
                                         data=payload.encode('ascii'),
                                         headers=headers,
                                         method='PUT')
            with urllib.request.urlopen(req, timeout=30) as response:
                the_page = response.read()
                # print("status:")
                # print(response.status)
        except ConnectionResetError:
            print("==> ConnectionResetError")
            pass
        except timeout: 
            print("==> Timeout")
            pass
        # response.status should be 200 here todo

def findDevices():
    devices = ssdp.discover("urn:schemas-konnected-io:device:Security:1")
    klist = []
    for d in devices:
       klist.append(konnected_dev(d))
    # print(klist)
    return klist

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf8'))
    )[20:24])

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

