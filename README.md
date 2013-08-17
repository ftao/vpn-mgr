vpn-mgr
=======

VPN Server Manage Tool 


Install
-----------------

by pip 
```
pip install -e git+https://github.com/ftao/vpn-mgr#egg=vpn-mgr
```

using git 
```
git clone https://github.com/ftao/vpn-mgr vpn-mgr
cd vpn-mgr
python setup.py install 
```

CLI Tool
-----------------

list active sessions 
```
vpnmgr-cli list 
```

kick some user offline 
```
vpnmgr-cli kick <USERNAME>
```

WebAPI
------------------
run a tiny web server 
```
vpnmgr-web 
```
Some enviroment variables are used by the web api server 

* VPNMGR_WEB_API_KEY
* VPNMGR_WEB_API_DEBUG

In production you may run 
```
VPNMGR_WEB_API_KEY=some-secretk0key  VPNMGR_WEB_API_DEBUG=0 vpnmgr-web
```

API Endpoints 

* `/session/list.<FORMAT>?k=<API_KEY>`  `FORMAT` can be  `json` or `html`
* `/session/disconnect/<USERNAME>?k=<API_KEY>`  `USERNAME` is the username to kick offline 



