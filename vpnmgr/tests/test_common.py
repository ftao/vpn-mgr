import unittest
import mock

from dateutil.tz import tzoffset
from vpnmgr.common import list_users



class TestCommon(unittest.TestCase):

    @mock.patch('vpnmgr.common.tzlocal')
    @mock.patch('vpnmgr.common.list_openvpn_servers')
    @mock.patch('vpnmgr.common.PPPServer.list_users')
    def test_list_user(self, m1, m2, m3):
        m1.return_value = [
           {'username': 'user1', 'tx': '2000', 'local_ip': '10.8.1.100',
             'rx': '1000', 'time': '2013-08-11 20:52', 
             'device': 'ppp0', 'type' : 'pptp', 'remote_ip': '9.9.9.9'}
        ]
        m2.return_value = []
        m3.return_value = tzoffset('Asia/Shanghai', 8 * 3600)
        users = list_users()

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['time'], '2013-08-11T20:52:00+08:00')
