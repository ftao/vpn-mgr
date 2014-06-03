"""VPN Management Agent

Usage:
  vpnmgr-agent.py --server=<server_address>

"""

import zmq
import time
import traceback
from docopt import docopt

from vpnmgr.common import list_users

def main():
    args = docopt(__doc__)
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.DEALER)
    socket.connect(args.get('--server'))

    while True:
        try:
            users = list_users()
            print('push users, total %d' % len(users))
            socket.send_json(users)
        except:
            traceback.print_exc()

        time.sleep(60)

if __name__ == '__main__':
    main()
