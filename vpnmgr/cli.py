"""VPN Management CLI

Usage:
  vpnmgr-cli.py list
  vpnmgr-cli.py kick CONN_ID
  vpnmgr-cli.py (-h | --help)

Arguments:
  CONN_ID   session to kill 

Options:
  -h --help               Show this screen.
"""

from docopt import docopt
import sys
from vpnmgr.common import list_users, kick_user

def main():
    args = docopt(__doc__)
    if args['list']:
        users = list_users()
        for user in users:
            print user
        sys.exit(0)
    elif args['kick']:
        conn_id = args['CONN_ID']
        if kick_user(conn_id):
            print 'user "%s" kicked' % conn_id
            sys.exit(0)
        else:
            print 'user "%s" not found' % conn_id
            sys.exit(-1)

if __name__ == '__main__':
    main()
