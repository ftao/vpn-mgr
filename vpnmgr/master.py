"""VPN Management Master

Usage:
  vpnmgr-master.py --listen=<server_address>

"""

import zmq
import json
from collections import defaultdict
from docopt import docopt

def main():
    args = docopt(__doc__)
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.ROUTER)
    socket.bind(args.get('--listen'))

    clients = defaultdict(lambda :{'users' : []})

    while True:
        parts = socket.recv_multipart()
        if len(parts) != 2:
            print("invalid msg count %d, expected 2" %len(parts))
            continue
        identify, msg = parts
        clients[identify]['users'] = json.loads(msg)
        display(clients)


def display(clients):
    for k,v in clients.items():
        print k, v

if __name__ == '__main__':
    main()
