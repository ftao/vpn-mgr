#!/usr/bin/env python
'''api main entrance'''
import web
import json
from vpnmgr.vpn.ppp import PPPServer
from vpnmgr.vpn.openvpn import list_openvpn_servers
from vpnmgr.config import OPENVPN_CONFIG_DIR

urls = (
  '/session/list\.(.*)', "list_sessions",
  '/session/disconnect/(.+)', "disconnect_session",
)

class list_sessions:

    def GET(self, fmt):
        users = PPPServer().list_users()
        for ovpn_server in list_openvpn_servers(OPENVPN_CONFIG_DIR):
            users += ovpn_server.list_users()

        if fmt == 'html':
            return self.render_html(users)
        else:
            return self.render_json(users)

    def render_json(self, users):
        return json.dumps(users, indent=2)

    def render_html(self, users):
        html = ['<html><body><table>']
        title = {
            'type' : 'type',
            'username' : 'username',
            'local_ip' : 'local_ip',
            'remote_ip' : 'remote_ip',
            'since' : 'since',
            'rx' : 'download',
            'tx' : 'upload',
        }
        row_template = '''
            <tr>
                <td>%(type)s</td>
                <td>%(username)s</td>
                <td>%(local_ip)s</td>
                <td>%(remote_ip)s</td>
                <td>%(since)s</td>
                <td>%(rx)s</td>
                <td>%(tx)s</td>
            </tr>
        '''
        html.append(row_template %title)
        for user in users:
            html.append(row_template % user)
        html.append("</table>")
        html.append("</html>")
        return "".join(html)

class disconnect_session:

    def GET(self, username):
        return {"ok" : self.do_disconnect(username)}

    def do_disconnect(self, username):
        ok = False
        if PPPServer().kick_user(username):
            ok = True
        else:
            for ovpn_server in list_openvpn_servers(OPENVPN_CONFIG_DIR):
                if ovpn_server.kick_user(username):
                    ok = True
                    break
        return ok

app = web.application(urls, globals())
#app.add_processor(auth_processor)

if __name__ == "__main__":
    app.run()
