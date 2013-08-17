"""VPN Management CLI

Usage:
  vpnmgr-cli.py list [-t TYPE] [-s SOCK]
  vpnmgr-cli.py kick [-t TYPE] [-s SOCK] NAME
  vpnmgr-cli.py (-h | --help)

Arguments:
  NAME     user to disconnect 

Options:
  -h --help               Show this screen.
  -t=TYPE --type=TYPE     all,pptp,l2tp,openvpn, [default: all]
  -s=SOCK --sock=SOCK     tcp or unix socket, for openvpn
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
        username = args['NAME']
        if kick_user(username):
            print 'user "%s" kicked' % username
            sys.exit(0)
        else:
            print 'user "%s" not found' % username
            sys.exit(-1)

if __name__ == '__main__':
    main()
