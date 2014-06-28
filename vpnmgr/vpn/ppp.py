#!/usr/bin/env python
'''PPP Based Server (PPTP/L2TP)
>>> import mock
>>> lines = """
... lo        Link encap:Local Loopback  
...           inet addr:127.0.0.1  Mask:255.0.0.0
...           inet6 addr: ::1/128 Scope:Host
...           UP LOOPBACK RUNNING  MTU:65536  Metric:1
...           RX packets:18261865 errors:0 dropped:0 overruns:0 frame:0
...           TX packets:18261865 errors:0 dropped:0 overruns:0 carrier:0
...           collisions:0 txqueuelen:0 
...           RX bytes:917050786 (917.0 MB)  TX bytes:917050786 (917.0 MB)
... 
... ppp0      Link encap:Point-to-Point Protocol  
...           inet addr:10.9.0.1  P-t-P:10.9.0.30  Mask:255.255.255.255
...           UP POINTOPOINT RUNNING NOARP MULTICAST  MTU:1500  Metric:1
...           RX packets:20144 errors:0 dropped:0 overruns:0 frame:0
...           TX packets:18000 errors:0 dropped:0 overruns:0 carrier:0
...           collisions:0 txqueuelen:3 
...           RX bytes:3670473 (3.6 MB)  TX bytes:9732393 (9.7 MB)
... 
... ppp1      Link encap:Point-to-Point Protocol  
...           inet addr:10.10.0.1  P-t-P:10.10.0.100  Mask:255.255.255.255
...           UP POINTOPOINT RUNNING NOARP MULTICAST  MTU:1496  Metric:1
...           RX packets:2234 errors:0 dropped:0 overruns:0 frame:0
...           TX packets:2093 errors:0 dropped:0 overruns:0 carrier:0
...           collisions:0 txqueuelen:3 
...           RX bytes:311373 (311.3 KB)  TX bytes:984397 (984.3 KB)
... """
>>> PPPServer._get_ifconfig_result = mock.Mock(return_value=lines)
>>> pptp_ip_range, l2tp_ip_range = ["10.10.0.100", "10.10.0.200"], ["10.9.0.2", "10.9.0.250"]
>>> intfs = PPPServer(pptp_ip_range, l2tp_ip_range)._list_interfaces()
>>> print len(intfs)
3
>>> print len([x for x in intfs if 'ptp' in x])
2
>>> print (intfs[1]['ptp'], intfs[2]['ptp'])
('10.9.0.30', '10.10.0.100')
>>> interfaces = [{'device' : 'ppp0', 'ptp' : '10.10.0.100', 'rxbytes' : '1000', 'txbytes' : '2000'}]
>>> expected = [{'service': 'pptp', 'rx': '1000', 'conn_id': 'ppp0', 'tx': '2000', 'virtual_ip': '10.10.0.100'}]
>>> PPPServer._list_interfaces = mock.Mock(return_value=interfaces)
>>> s = PPPServer(pptp_ip_range, l2tp_ip_range)
>>> s.list_users() == expected
True
>>> line = "root     14509  0.0  0.0  27852  1456 pts/38   Ss+  20:58   0:00 /usr/sbin/pppd local file /etc/ppp/pptpd-options 115200 10.10.0.1:10.10.0.133 ipparam 9.9.9.9 plugin /usr/lib/pptpd/pptpd-logwtmp.so pptpd-original-ip 9.9.9.9"
>>> @mock.patch('subprocess.check_output', lambda y,**kwargs:line)
... def test_find_pid_by_ip():
...     print s._find_pid_by_ip('10.10.0.133')
>>> test_find_pid_by_ip()
14509
>>> line = ""
>>> @mock.patch('subprocess.check_output', lambda y, **kwargs:line)
... def test_find_pid_by_ip():
...     print s._find_pid_by_ip('10.10.0.133')
>>> test_find_pid_by_ip()
None
'''

import os
import re
import signal
import subprocess
from vpnmgr.util import is_ip_in_range
from vpnmgr.vpn.base import BaseVPNServer

class PPPServer(BaseVPNServer):

    def __init__(self, pptp_ip_range, l2tp_ip_range):
        self.pptp_ip_range = pptp_ip_range
        self.l2tp_ip_range = l2tp_ip_range

    def list_users(self):
        interfaces = self._list_interfaces()
        #when pptp is being setup, 'ptp' is None, ignore them
        interfaces = filter(lambda intf: 'ppp' in intf['device'] and intf.get('ptp'), interfaces)
        users = []
        for interface in interfaces:
            user = {
                'conn_id' : interface['device'],
                'virtual_ip' : interface['ptp'],
                'rx' : interface['rxbytes'],
                'tx' : interface['txbytes'],
            }
            user['service'] = self._decide_type(user)
            users.append(user)
        return users

    def _disconnect_by_conn_id(self, conn_id):
        ip = self._find_ip_by_conn_id(conn_id)
        return self._disconnect_by_ip(ip)

    def _disconnect_by_ip(self, ip):
        pid = self._find_pid_by_ip(ip)
        if pid:
            return 0 == os.kill(pid, signal.SIGKILL)
        return False

    def _decide_type(self, user):
        ip = user['virtual_ip']
        if is_ip_in_range(ip, self.pptp_ip_range):
            return 'pptp'
        elif is_ip_in_range(ip, self.l2tp_ip_range):
            return 'l2tp'
        else:
            return 'ppp'

    def _get_ifconfig_result(self):
        return subprocess.check_output('ifconfig', shell=True)
        
    def _list_interfaces(self):
        return self._parse_ifconfig_result(self._get_ifconfig_result())

    def _parse_ifconfig_result(self, text):
        start_pattern = '(?P<device>^[a-zA-Z0-9:]+)(.*)Link encap:(.*).*'
        patterns = [
            '.*(inet addr:)(?P<inet>[^\s]*).*',
            '.*(P-t-P:)(?P<ptp>[^\s]*).*',
            '.*(RX bytes:)(?P<rxbytes>\d+).*',
            '.*(TX bytes:)(?P<txbytes>\d+).*',
        ]
        interfaces = []
        last_record = {}
        for line in text.split("\n"):
            match = re.search(start_pattern, line)
            if match:
                if last_record:
                    interfaces.append(last_record)
                last_record = match.groupdict()
                continue
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    last_record.update(match.groupdict())       
        if last_record:
            interfaces.append(last_record)
        return interfaces
                
    def _find_pid_by_ip(self, ip):
        line =  subprocess.check_output('ps aux | grep "^root.*/usr/sbin/pppd.*%s"' %ip, shell=True)
        if line == "":
            return None
        return int(line.split()[1])

    def _find_ip_by_conn_id(self, conn_id):
        users = self.list_users()
        for user in users:
            if user['conn_id'] == conn_id:
                return user['virtual_ip']
