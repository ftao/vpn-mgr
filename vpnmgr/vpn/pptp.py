#!/usr/bin/env python
'''PPTP'''
import logging
from vpnmgr.util import is_ip_in_range, parse_ip_line

logger = logging.getLogger()

DEFAULT_PPTP_CONF_PATH = '/etc/pptpd.conf'

class PPTPConfParser(object):

    @staticmethod
    def parse_file(path):
        with open(path, 'r') as fp:
            return PPTPConfParser.parse_text(fp.read())

    @staticmethod
    def parse_text(text):
        '''
        >>> text = """
        ... localip  10.10.0.1
        ... remoteip 10.10.0.100-200
        ... """ 
        >>> PPTPConfParser.parse_text(text)
        {'remote_ip': [('10.10.0.100', '10.10.0.200')], 'local_ip': ['10.10.0.1']}
        >>> text = """
        ... localip 192.168.0.234-238,192.168.0.245
        ... remoteip 192.168.1.234-238,192.168.1.245
        ... """ 
        >>> PPTPConfParser.parse_text(text)
        {'remote_ip': [('192.168.1.234', '192.168.1.238'), '192.168.1.245'], 'local_ip': [('192.168.0.234', '192.168.0.238'), '192.168.0.245']}
        '''
        conf = {}
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith("localip"):
                conf['local_ip']= parse_ip_line(line.split(None, 1)[1])
            elif line.startswith("remoteip"):
                conf['remote_ip']= parse_ip_line(line.split(None, 1)[1])
        return conf


def is_pptp_ip(ip, pptp_conf_path=DEFAULT_PPTP_CONF_PATH):
    conf = PPTPConfParser().parse_file(pptp_conf_path)
    return is_ip_in_range(ip, conf.get('remote_ip', []))

