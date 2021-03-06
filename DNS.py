# Copyright (C) 2018 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dnslib.server import DNSServer
from dnslib.zoneresolver import ZoneResolver
from jinja2 import Template

import netifaces


class DNS(object):
    def __init__(self):
        default_gw_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        default_ip = netifaces.ifaddresses(default_gw_interface)[netifaces.AF_INET][0]['addr']
        self.default_ip = default_ip
        self.resolver = None
        self.server = None
        self.base_zone_data = None
        self.reset()

    def load_zone(self, api_version):
        zone_file = open("test_data/IS0401/dns_records.zone").read()
        template = Template(zone_file)
        zone_data = template.render(ip_address=self.default_ip, api_ver=api_version)
        self.resolver = ZoneResolver(self.base_zone_data + zone_data)
        self.stop()
        self.start()

    def reset(self):
        zone_file = open("test_data/IS0401/dns_base.zone").read()
        template = Template(zone_file)
        self.base_zone_data = template.render(ip_address=self.default_ip)
        self.resolver = ZoneResolver(self.base_zone_data)
        self.stop()
        self.start()

    def start(self):
        if not self.server:
            print(" * Starting DNS server on {}:53".format(self.default_ip))
            try:
                self.server = DNSServer(self.resolver, port=53, address=self.default_ip)
                self.server.start_thread()
            except Exception as e:
                print(" * ERROR: Unable to bind to port 53. DNS server could not start: {}".format(e))

    def stop(self):
        if self.server:
            self.server.stop()
            self.server = None
