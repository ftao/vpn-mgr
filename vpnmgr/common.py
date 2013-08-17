from vpnmgr.config import OPENVPN_CONFIG_DIR
from vpnmgr.vpn.ppp import PPPServer
from vpnmgr.vpn.openvpn import list_openvpn_servers

def list_users():
    users = PPPServer().list_users()
    for ovpn_server in list_openvpn_servers(OPENVPN_CONFIG_DIR):
        users += ovpn_server.list_users()
    return users

def kick_user(username):
    ok = False
    if PPPServer().kick_user(username):
        ok = True
    else:
        for ovpn_server in list_openvpn_servers(OPENVPN_CONFIG_DIR):
            if ovpn_server.kick_user(username):
                ok = True
                break
    return ok


