#!/usr/bin/env python
'''L2TP'''
import logging
from vpnmgr.util import is_ip_in_range, parse_ip_line

logger = logging.getLogger()

DEFAULT_L2TP_CONF_PATH = '/etc/xl2tpd/xl2tpd.conf'

class L2TPConfParser(object):

    @staticmethod
    def parse_file(path):
        with open(path, 'r') as fp:
            return L2TPConfParser.parse_text(fp.read())

    @staticmethod
    def parse_text(text):
        '''
        >>> text = """
        ... [lns default]
        ... local ip = 10.9.0.1
        ... ip range = 10.9.0.30-250
        ... length bit = yes
        ... """ 
        >>> L2TPConfParser.parse_text(text)
        {'remote_ip': [('10.9.0.30', '10.9.0.250')], 'local_ip': ['10.9.0.1']}
        '''
        conf = {}
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith("local ip"):
                conf['local_ip']= parse_ip_line(line.split("=", 1)[1])
            elif line.startswith("ip range"):
                conf['remote_ip']= parse_ip_line(line.split("=", 1)[1])
        return conf


def is_l2tp_ip(ip, l2tp_conf_path=DEFAULT_L2TP_CONF_PATH):
    conf = L2TPConfParser().parse_file(l2tp_conf_path)
    return is_ip_in_range(ip, conf.get('remote_ip', []))

