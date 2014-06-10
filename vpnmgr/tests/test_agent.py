import json
import unittest
import mock
from vpnmgr.agent import VPNNode

class TestVPNNode(unittest.TestCase):

    @mock.patch("vpnmgr.agent.Node.send")
    @mock.patch("vpnmgr.agent.list_users")
    def test_pull_state(self, list_user_mock, send_mock):
        list_user_mock.return_value = []

        n = VPNNode('n1', None)

        msg = {
            'nid' : 'master',
            'action' : 'pull_state',
        }
        n.handle_msg([json.dumps(msg)])

        send_mock.assert_called_once_with([
            json.dumps({"action": "share_state", "state": {"users": []}, "nid": "n1"})
        ])


    @mock.patch("vpnmgr.agent.Node.send")
    @mock.patch("vpnmgr.agent.kick_user")
    def test_pull_state(self, kick_user_mock, send_mock):
        n = VPNNode('n1', None)
        msg = {
            'action' : 'kick',
            'username' : 'test1',
        }
        n.handle_msg([json.dumps(msg)])
        self.assertFalse(send_mock.called)
        
        kick_user_mock.assert_called_once_with('test1')

