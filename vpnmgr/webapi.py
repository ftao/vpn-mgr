#!/usr/bin/env python
'''api main entrance'''
import web
import json
from vpnmgr.common import list_users, kick_user
from vpnmgr import config

urls = (
  '/session/list\.(.*)', "list_sessions",
  '/session/disconnect/(.+)', "disconnect_session",
)

def auth_processor(handler): 
    query = web.input()
    k = query.get('k', '')
    if k != config.API_KEY:
        return web.Forbidden()
    else:
        return handler()

class list_sessions:

    def GET(self, fmt):
        users = list_users()
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
        return {"ok" : kick_user(username)}

app = web.application(urls, globals())
app.add_processor(auth_processor)

def main():
    web.config.debug = config.DEBUG
    app.run()

if __name__ == "__main__":
    main()
