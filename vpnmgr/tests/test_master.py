import json
import unittest
import mock
from vpnmgr.master import MasterNode

class TestMasterNode(unittest.TestCase):

    def test_register(self):
        n = MasterNode('master', None)
        msg = {
            'nid' : 'vpnnode',
            'action' : 'register',
        }
        n.handle_msg(['c1', json.dumps(msg)])
        self.assertEqual(len(n._nodes), 1)
        self.assertTrue('vpnnode' in n._nodes)
        self.assertEqual(n._nodes['vpnnode']['meta']['cid'], 'c1') 


    def test_share_state(self):
        n = MasterNode('master', None)

        user= {
            'username': 'user1', 'tx': '2000', 'local_ip': '10.8.1.100',
            'rx': '1000', 'time': '2013-08-11T20:52+08:00', 
            'device': 'ppp0', 'type' : 'pptp', 'remote_ip': '9.9.9.9'
        }
 
        msg = {
            'nid' : 'vpnnode',
            'action' : 'share_state',
            'state' : {
                'users' : [user]
            }
        }
        n.handle_msg(['c1', json.dumps(msg)])

        self.assertEqual(len(n._nodes), 1)
        self.assertTrue('vpnnode' in n._nodes)
        self.assertEqual(n._nodes['vpnnode']['meta']['cid'], 'c1') 

    @mock.patch('time.time')
    def test_check_offline(self, m1):
        m1.return_value = 60

        n = MasterNode('master', None)
        user= {
            'username': 'user1', 'tx': '2000', 'local_ip': '10.8.1.100',
            'rx': '1000', 'time': '2013-08-11T20:52+08:00', 
            'device': 'ppp0', 'type' : 'pptp', 'remote_ip': '9.9.9.9'
        }
        msg = {
            'nid' : 'vpnnode',
            'action' : 'share_state',
            'state' : {
                'users' : [user]
            }
        }
        n.handle_msg(['c1', json.dumps(msg)])

        self.assertEqual(n._nodes['vpnnode']['meta']['last_update'], 60)

        m1.return_value = 60 + n.node_offline_timeout + 1

        n._check_offline_nodes(n._nodes)

        self.assertEqual(len(n._nodes), 0)


    def test_check_duplicate(self):
        n = MasterNode('master', None)

        user= {
            'username': 'user1', 'tx': '2000', 'local_ip': '10.8.1.100',
            'rx': '1000', 'time': '2013-08-11T20:52+08:00', 
            'device': 'ppp0', 'type' : 'pptp', 'remote_ip': '9.9.9.9'
        }
 
        msg = {
            'nid' : 'vpnnode',
            'action' : 'share_state',
            'state' : {
                'users' : [user]
            }
        }
        n.handle_msg(['c1', json.dumps(msg)])

        msg['nid'] = 'vpnnode2'
        user['time'] = '2013-08-11T20:53+08:00'
        n.handle_msg(['c2', json.dumps(msg)])

        self.assertEqual(len(n._nodes), 2)

        result = list(n._check_duplicate(n._nodes))
        self.assertEqual(result, [(u'vpnnode', u'user1')])
