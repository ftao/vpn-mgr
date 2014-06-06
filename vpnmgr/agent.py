"""VPN Management Agent

Usage:
  vpnmgr-agent.py --server=<server_address> [--id=<node_id>]

"""

import time
import json
import logging
import zmq
from docopt import docopt
from vpnmgr.common import list_users, kick_user
from vpnmgr.node import Node
from vpnmgr.log import setup_logging

class VPNNode(Node):
    push_interval = 30

    def __init__(self, nid, socket):
        super(VPNNode, self).__init__(nid, socket)
        self._last_report = 0

    def handle_idle(self):
        now = time.time()
        if now - self._last_report < self.push_interval:
            return
        self._report()
        self._last_report = now

    def handle_msg(self, msg):
        if len(msg) != 1:
            raise Exception("msg should contains 1 frames")
        self._handle_command(json.loads(msg[0]))

    def _handle_command(self, msg):
        if msg['action'] == 'kick':
            ok = kick_user(msg['username'])
            logging.info("kick user %s result %s", msg['username'], ok)

    def _report(self):
        users = list_users()
        self.send([json.dumps({
            'action' : 'share_state', 
            'nid' : self.nid, 
            'state' : {
                'users' : users
            }})])
        logging.info("push %d users to server", len(users))

def main():
    args = docopt(__doc__)
    setup_logging()

    addr = args.get('--server')
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.DEALER)
    socket.connect(addr)

    nid = args.get('--id') or 'vpnnode'
    agent = VPNNode(nid, socket)
    logging.info("start agent, connect to %s", addr)
    agent.run()

if __name__ == '__main__':
    main()
