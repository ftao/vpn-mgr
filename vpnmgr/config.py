import os
OPENVPN_CONFIG_DIR = '/etc/openvpn/'
API_KEY = os.environ.get('VPNMGR_WEB_API_KEY', 'default-vpnmgr-key-b80a')
DEBUG = os.environ.get('VPNMGR_WEB_API_DEBUG', '1') == '1'
