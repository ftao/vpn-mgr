#!/usr/bin/env python
'''IPSec
>>> lines = """Security Associations (1 up, 0 connecting):
...     ikev1[88]: ESTABLISHED 6 seconds ago, 162.243.155.198[162.243.155.198]...101.80.25.230[192.168.254.100]
...     ikev1[88]: Remote XAuth identity: demo
...     ikev1{62}:  INSTALLED, TUNNEL, ESP in UDP SPIs: cbb9eab5_i 05b570b0_o
...     ikev1{62}:  AES_CBC_128/HMAC_SHA1_96, 435707 bytes_i (6220 pkts, 2s ago), 9856463 bytes_o (8394 pkts, 2s ago), rekeying in 8 minutes
...     ikev1{62}:   0.0.0.0/0 === 10.7.0.1/32 
...     ikev1[89]: ESTABLISHED 10 seconds ago, 162.243.155.198[162.243.155.198]...101.39.25.230[192.168.254.101]
...     ikev1[89]: Remote XAuth identity: test
...     ikev1{63}:  INSTALLED, TUNNEL, ESP in UDP SPIs: cbb9eab5_i 05b570b0_o
...     ikev1{63}:  AES_CBC_128/HMAC_SHA1_96, 435707 bytes_i (6220 pkts, 2s ago), 9856463 bytes_o (8394 pkts, 2s ago), rekeying in 8 minutes
...     ikev1{63}:   0.0.0.0/0 === 10.7.0.2/32 
... """
>>> import mock
>>> IPSecServer._get_ipsec_status = mock.Mock(return_value=lines)
>>> server = IPSecServer("ikev1")
>>> users = server.list_users()
>>> print len(users)
2
>>> print users[0]
{'username': 'demo', 'service': 'ipsec.ikev1', 'tx': 9856463, 'rx': 435707, 'conn_id': 'ikev1[88]', 'virtual_ip': '10.7.0.1', 'remote_ip': '101.80.25.230'}
>>> print users[1]['username']
test
>>> #test no ip assigned
>>> lines = """Security Associations (1 up, 0 connecting):
...     ikev1[88]: ESTABLISHED 6 seconds ago, 162.243.155.198[162.243.155.198]...101.80.25.230[192.168.254.100]
...     ikev1[88]: Remote XAuth identity: demo
...     ikev1{62}:  INSTALLED, TUNNEL, ESP in UDP SPIs: cbb9eab5_i 05b570b0_o
...     ikev1{62}:  AES_CBC_128/HMAC_SHA1_96, 435707 bytes_i (6220 pkts, 2s ago), 9856463 bytes_o (8394 pkts, 2s ago), rekeying in 8 minutes
... """
>>> import mock
>>> IPSecServer._get_ipsec_status = mock.Mock(return_value=lines)
>>> users = IPSecServer("ikev1").list_users()
>>> print len(users)
0
'''
import re
import subprocess
from vpnmgr.vpn.base import BaseVPNServer

IPSEC_BIN = '/usr/sbin/ipsec'

class IPSecServer(BaseVPNServer):
    "IPSEC Server"

    def __init__(self, ipsec_conf_name="ikev1"):
        self.ipsec_conf_name = ipsec_conf_name

    def list_users(self):
        text = self._get_ipsec_status()
        users = self._parse_ipsec_status_output(text, self.ipsec_conf_name)

        for user in users:
            user.update({
                "service" : "ipsec.%s" % self.ipsec_conf_name,
            })

        return users

    def _disconnect_by_conn_id(self, conn_id):
        return 0 == subprocess.call([IPSEC_BIN, "down", conn_id], shell=True)

    def _get_ipsec_status(self):
        return subprocess.check_output([IPSEC_BIN, "statusall", self.ipsec_conf_name], shell=True)

    @staticmethod
    def _parse_ipsec_status_output(text, ipsec_conf_name):
        lines = text.split("\n")
        records = []
        last_record = None
        ip_reg = re.compile("(\d+(\.\d+){3})")

        username_keyworkd = "Remote XAuth identity:"

        for line in lines:
            if ipsec_conf_name not in line:
                continue

            if "ESTABLISHED" in line:
                conn_id = line.split(":", 1)[0].strip()
                ips = ip_reg.findall(line)
                if len(ips) == 4:
                    last_record = {
                        "conn_id" : conn_id,
                        "remote_ip" : ips[2][0],
                    }

            if last_record is None:
                continue

            iobytes = re.findall(" (\d+) bytes_([io])", line)
            for item in iobytes:
                if item[1] == "i":
                    last_record["rx"] = int(item[0])
                else:
                    last_record["tx"] = int(item[0])

            if username_keyworkd in line:
                last_record['username'] = line[line.find(username_keyworkd) + len(username_keyworkd):].strip()

            if "===" in line:
                ips = ip_reg.findall(line)
                if len(ips) == 2:
                    last_record["virtual_ip"] = ips[1][0]

                    records.append(last_record)
                    last_record = None
        return records
