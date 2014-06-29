from dateutil.parser import parse
from dateutil.tz import tzlocal
from vpnmgr.vpn.ppp import PPPServer
from vpnmgr.vpn.openvpn import OpenVPNServer
from vpnmgr.vpn.ipsec import IPSecServer
from vpnmgr.config import get_config
import logging

def list_services(conf):
    return [
        PPPServer(conf['pptp_ip_range'], conf['l2tp_ip_range'])
    ] + [
        OpenVPNServer(item['name'], item['endpoint']).list_users()
        for item in conf['openvpn_instances']
    ] + [
        IPSecServer(item) for item in conf['ipsec_instances']
    ]

def list_users():
    conf = get_config()
    users = []
    for service in list_services(conf):
        try:
            users = users + service.list_users()
        except:
            logging.exception("fail to list users for %s", service)
    for user in users:
        if 'time' in user:
            user['time'] = parse(user['time']).replace(tzinfo=tzlocal()).isoformat()
    return users

def kick_user(conn_id=None, virtual_ip=None):
    conf = get_config()
    for service in list_services(conf):
        try:
            if service.kick_user(conn_id, virtual_ip):
                return True
        except:
            logging.exception("fail to kick for service %s", service)
    return False
