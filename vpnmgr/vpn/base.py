'''
Common Interface for VPN Server Instance
'''

class BaseVPNServer(object):

    def list_users(self):
        return []

    def kick_user(self, conn_id=None, ip=None):
        assert conn_id is not None or ip is not None
        if conn_id is not None:
            if self._disconnect_by_conn_id(conn_id):
                return True
        if ip is not None:
            if self._disconnect_by_ip(ip):
                return True
        return False

    def _disconnect_by_conn_id(self):
        return False

    def _disconnect_by_ip(self):
        return False
