#!/usr/bin/env python
'''PPP Based VPN Server'''
import sys
import os
import re
import subprocess
import ifcfg
from vpnmgr.vpn.pptp import is_pptp_ip
from vpnmgr.vpn.l2tp import is_l2tp_ip

class PPPServer(object):
    '''PPP Based Server (PPTP/L2TP)
    >>> import mock
    >>> interfaces = [{'device' : 'ppp0', 'ptp' : '10.8.1.100', 'rxbytes' : '1000', 'txbytes' : '2000'}]
    >>> wtmp_records = "user1 ppp0        2013-08-11 20:52 (9.9.9.9)"
    >>> expected = [
    ...    {'username': 'user1', 'tx': '2000', 'local_ip': '10.8.1.100',
    ...     'rx': '1000', 'time': '2013-08-11 20:52', 
    ...     'device': 'ppp0', 'type' : 'pptp', 'remote_ip': '9.9.9.9'}]
    >>> @mock.patch.object(PPPServer, '_list_interfaces', lambda x:interfaces)
    ... @mock.patch.object(PPPServer, '_get_wtmp_record', lambda x:wtmp_records)
    ... @mock.patch.object(PPPServer, '_decide_type', lambda x,user:'pptp')
    ... def test_list_user():
    ...     return expected == PPPServer().list_users()
    >>> test_list_user()
    True
    '''

    def list_users(self):
        interfaces = self._list_interfaces()
        #when pptp is being setup, 'ptp' is None, ignore them
        interfaces = filter(lambda intf: 'ppp' in intf['device'] and intf.get('ptp'), interfaces)
        users = []
        for interface in interfaces:
            user = {
                'device' : interface['device'],
                'local_ip' : interface['ptp'],
                'rx' : interface['rxbytes'],
                'tx' : interface['txbytes'],
            }
            user['type'] = self._decide_type(user)
            users.append(user)

        device_map = self._build_device_username_ip_map()

        for user in users:
            user.update(device_map.get(user['device'], {}))

        return users

    def kick_user(self, username):
        ip = self._find_local_ip_by_username(username)
        if ip is not None:
            pid = self._find_pid_by_ip(ip)
            if pid:
                return 0 == os.kill(pid)
        return False

    def _decide_type(self, user):
        if is_pptp_ip(user['local_ip']):
            return 'pptp'
        elif is_l2tp_ip(user['local_ip']):
            return 'l2tp'
        else:
            return 'ppp'

    def _list_interfaces(self):
        return ifcfg.interfaces().values()

    def _get_wtmp_record(self):
        path = '/var/log/wtmp'
        try:
            return subprocess.check_output('who %s | grep ppp' % path, shell=True)
        except:
            sys.stderr.write('fail to read or parse ppp login record from %s\n' % path)
            return ''

    def _build_device_username_ip_map(self):
        '''
        build a map from device to remote ip and username
        '''
        lines = self._get_wtmp_record()
        records = self._parse_wtmp_output(lines)
        device_map = {}
        for rec in records:
            device_map[rec['device']] = rec
        return device_map

    @staticmethod
    def _parse_wtmp_output(text):
        '''
        >>> lines = """user1 ppp34        2013-08-11 20:52 (9.9.9.9)
        ... user2.xz ppp14        2013-08-11 20:52 (211.211.211.211)
        ... """
        >>> records = PPPServer._parse_wtmp_output(lines)
        >>> print records[0]
        {'username': 'user1', 'device': 'ppp34', 'time': '2013-08-11 20:52', 'remote_ip': '9.9.9.9'}
        >>> print records[1]
        {'username': 'user2.xz', 'device': 'ppp14', 'time': '2013-08-11 20:52', 'remote_ip': '211.211.211.211'}
        >>> lines = """demo  ppp0         Aug  1 15:56 (211.211.211.211)"""
        >>> records = PPPServer._parse_wtmp_output(lines)
        >>> print records[0]
        {'username': 'demo', 'device': 'ppp0', 'time': 'Aug  1 15:56', 'remote_ip': '211.211.211.211'}
        '''
        pattern = re.compile(r'^(?P<username>[\w.]+)\s+(?P<device>\w+)\s+(?P<time>[a-zA-Z\d\- :]+)\s*\((?P<remote_ip>[0-9.]+)\)')
        records = []
        for line in text.split('\n'):
            line = line.strip()
            match = pattern.match(line)
            if match:
                group = match.groupdict()
                group['time'] = group['time'].strip()
                records.append(group)
        return records


    def _find_pid_by_ip(self, ip):
        '''
        >>> import mock
        >>> line = "root     14509  0.0  0.0  27852  1456 pts/38   Ss+  20:58   0:00 /usr/sbin/pppd local file /etc/ppp/pptpd-options 115200 10.10.0.1:10.10.0.133 ipparam 9.9.9.9 plugin /usr/lib/pptpd/pptpd-logwtmp.so pptpd-original-ip 9.9.9.9"
        >>> @mock.patch('subprocess.check_output', lambda y,**kwargs:line)
        ... def test_find_pid_by_ip():
        ...     print PPPServer()._find_pid_by_ip('10.10.0.133')
        >>> test_find_pid_by_ip()
        14509
        >>> line = ""
        >>> @mock.patch('subprocess.check_output', lambda y, **kwargs:line)
        ... def test_find_pid_by_ip():
        ...     print PPPServer()._find_pid_by_ip('10.10.0.133')
        >>> test_find_pid_by_ip()
        None
        '''
        line =  subprocess.check_output('ps aux | grep "^root.*/usr/sbin/pppd.*%s"' %ip, shell=True)
        if line == "":
            return None
        return int(line.split()[1])

    def _find_local_ip_by_username(self, username):
        users = self.list_users()
        for user in users:
            if user['username'] == username:
                return user['local_ip']

