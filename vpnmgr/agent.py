"""VPN Management Agent

Usage:
  vpnmgr-agent.py --server=<server_address>

"""

import json
import logging
import traceback
import zmq
from docopt import docopt
from vpnmgr.common import list_users, kick_user
from vpnmgr.node import Node
from vpnmgr.log import setup_logging

class VPNNode(Node):
    push_interval = 30

    def run(self):
        while True:
            self._report()
            item = self.poll(timeout=self.push_interval * 1000)
            if item is not None:
                try:
                    self._handle_command(json.loads(item[0]))
                except:
                    logging.exception("fail to handle command")
                    traceback.print_exc()

    def _handle_command(self, msg):
        if msg['action'] == 'kick':
            ok = kick_user(msg['username'])
            logging.info("kick user %s result %s", msg['username'], ok)

    def _report(self):
        try:
            users = list_users()
            self.send([json.dumps({'users' : users})])
            logging.info("push %d users to server", len(users))
        except:
            traceback.print_exc()

def main():
    args = docopt(__doc__)
    setup_logging()

    addr = args.get('--server')
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.DEALER)
    socket.connect(addr)

    agent = VPNNode(socket)
    logging.info("start agent, connect to %s", addr)
    agent.run()

if __name__ == '__main__':
    main()
