"""VPN Management Master

Usage:
  vpnmgr-master.py --listen=<server_address>

"""

import time
import json
import logging
from collections import defaultdict
from docopt import docopt
from dateutil.parser import parse
import zmq
from vpnmgr.node import Node
from vpnmgr.log import setup_logging

class MasterNode(Node):
    node_offline_timeout = 600
    node_pull_interval = 60

    def __init__(self, nid, socket):
        super(MasterNode, self).__init__(nid, socket)
        self._nodes = defaultdict(lambda : {'meta' : {}, 'data' : {}})
        self._node_connections = {}

    def handle_msg(self, msg):
        if len(msg) != 2:
            raise Exception("msg should contains 2 frames")
        cid, data = msg
        data = json.loads(data)
        if data['action'] == 'register':
            self._handle_register(cid, data)
        elif data['action'] == 'share_state':
            self._update_state(cid, data)

    def handle_idle(self):
        self._check_offline_nodes(self._nodes)
        for nid, username in self._check_duplicate(self._nodes):
            self._kick_node_user(nid, username)
        self._pull_state(self._nodes)

    def _handle_register(self, cid, info):
        nid = info.get('nid')
        logging.info("register node nid=%s cid=%s", nid, cid)
        self._nodes[nid]['meta'].update({
            'nid' : nid,
            'cid' : cid,
            'register_time' : time.time()
        })

    def _update_state(self, cid, info):
        nid = info.get('nid')
        logging.info("update node %s %s", nid, info)
        self._nodes[nid]['state'] = info['state']
        self._nodes[nid]['meta'].update({
            'last_update' : time.time(),
            'cid' : cid,
            'nid' : nid,
        })

    def _pull_state(self, nodes):
        now = time.time()
        for nid, v in nodes.iteritems():
            last_pull_or_update = max(v['meta'].get('last_pull', 0) or v['meta'].get('last_update'))
            if last_pull_or_update + self.node_pull_interval <= now:
                cid = self._nodes[nid]['meta']['cid']
                self.send([
                    cid,
                    json.dumps({"action" : "pull_state", "nid" : nid})
                ])
                v['last_pull'] = now

    def _kick_node_user(self, nid, username):
        logging.info("kick user %s from node %s", username, nid)
        cid = self._nodes[nid]['meta']['cid']
        self.send([
            cid,
            json.dumps({"action" : "kick", "username" : username})
        ])

    def _check_offline_nodes(self, nodes):
        now = time.time()
        offline_nodes = []
        for nid, v in nodes.iteritems():
            last_active = max(v['meta'].get('last_update', 0), v['meta'].get('register_time', 0))
            if last_active + self.node_offline_timeout < now:
                offline_nodes.append(nid)
        for nid in offline_nodes:
            del nodes[nid]

    def _check_duplicate(self, nodes):
        user_at_nodes = defaultdict(lambda : [])
        for nid, v in nodes.iteritems():
            users = v.get('state', {}).get('users', [])
            for user in users:
                user_at_nodes[user['username']].append({
                    'nid' : nid,
                    'login_time' : time.mktime(parse(user['time']).timetuple()),
                })
        for username, unodes in user_at_nodes.iteritems():
            if len(unodes) <= 1:
                continue
            unodes = sorted(unodes, key=lambda x:x.get('login_time'))
            for item in unodes[:-1]:
                yield (item['nid'], username)

def main():
    args = docopt(__doc__)
    setup_logging()

    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.ROUTER)
    endpoint = args.get('--listen')
    socket.bind(endpoint)

    logging.info("start master, listen %s", endpoint)
    master = MasterNode('master', socket)
    master.run()

if __name__ == '__main__':
    main()
