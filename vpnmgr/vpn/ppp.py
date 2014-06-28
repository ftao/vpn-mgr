#!/usr/bin/env python
'''PPP Based Server (PPTP/L2TP)
>>> import mock
>>> pptp_ip_range, l2tp_ip_range = ["10.10.0.100", "10.10.0.200"], ["10.9.0.2", "10.9.0.250"]
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
import subprocess
import ifcfg
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

    def _disconnect_by_ip(self, ip):
        pid = self._find_pid_by_ip(ip)
        if pid:
            return 0 == os.kill(pid)
        return False

    def _decide_type(self, user):
        ip = user['virtual_ip']
        if is_ip_in_range(ip, self.pptp_ip_range):
            return 'pptp'
        elif is_ip_in_range(ip, self.l2tp_ip_range):
            return 'l2tp'
        else:
            return 'ppp'

    def _list_interfaces(self):
        return ifcfg.interfaces().values()

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
