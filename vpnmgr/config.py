import yaml
import os
DEFAULSTS = {
    "pptp_ip_range": ["10.10.0.1", "10.10.0.255"],
    "l2tp_ip_range": ["10.9.0.1", "10.9.0.255"],
    "ipsec_instances": ["ikev1"],
    "openvpn_instances": [],
}

conf_search_path = [
    os.path.join(os.getcwd(), "vpnmgr.yml"),
    os.path.expandvars("~/.vpnmgr.yml"),
    os.path.expandvars("/etc/vpnmgr.yml"),
]
def get_config(conf_path=None):
    conf = {}
    conf.update(DEFAULSTS)
    if conf_path is not None:
        with open(conf_path, 'r') as fp:
            conf.update(yaml.load(fp))

    else:
        for path in conf_search_path:
            if not os.path.exists(path):
                continue
            with open(path, 'r') as fp:
                conf.update(yaml.load(fp))
    return conf

