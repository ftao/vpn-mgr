"""VPN Management Master

Usage:
  vpnmgr-master.py --listen=<server_address>

"""

import time
import json
import logging
from collections import defaultdict
from docopt import docopt
import zmq
from vpnmgr.node import Node
from vpnmgr.log import setup_logging

class MasterNode(Node):
    node_offline_timeout = 600

    def __init__(self, socket):
        super(MasterNode, self).__init__(socket)
        self._nodes = defaultdict(lambda : {})

    def run(self):
        nodes = self._nodes
        while True:
            item = self.poll(timeout=5000)
            if item is not None:
                try:
                    identify, msg = item
                    self._update_node(identify, json.loads(msg))
                except:
                    logging.exception("fail to handle msg")

            self._check_offline_nodes(nodes)
            for nid, username in self._check_duplicate(nodes):
                self._kick_node_user(nid, username)

    def _update_node(self, nid, info):
        logging.info("update node %s", nid)
        self._nodes[nid].update(info)
        self._nodes[nid].update({'last_update' : time.time()})

    def _kick_node_user(self, nid, username):
        logging.info("kick user %s from node %s", username, nid)
        self.send([
            nid,
            json.dumps({"action" : "kick", "username" : username})
        ])

    def _check_offline_nodes(self, nodes):
        now = time.time()
        offline_nodes = []
        for nid, v in nodes.iteritems():
            if v.get('last_update', 0) + self.node_offline_timeout < now:
                offline_nodes.append(nid)

        for nid in offline_nodes:
            del nodes[nid]

    def _check_duplicate(self, nodes):
        user_at_nodes = defaultdict(lambda : [])
        for nid, v in nodes.iteritems():
            for user in v.get('users', []):
                user_at_nodes[user['username']].append({
                    'nid' : nid,
                    'login_time' : user['time'],
                    'last_update' : v.get('last_update')
                })
        for username, unodes in user_at_nodes.iteritems():
            if len(unodes) <= 1:
                continue
            unodes = sorted(unodes, lambda x:x['login_time'])
            for item in unodes[1:]:
                yield (item['nid'], username)

def main():
    args = docopt(__doc__)
    setup_logging()

    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.ROUTER)
    endpoint = args.get('--listen')
    socket.bind(endpoint)

    logging.info("start master, listen %s", endpoint)
    master = MasterNode(socket)
    master.run()

if __name__ == '__main__':
    main()
