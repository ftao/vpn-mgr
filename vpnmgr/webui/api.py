#!/usr/bin/env python
'''api main entrance'''
import web
import json
from vpnmgr.common import list_users, kick_user

urls = (
  '/api/connection/list/', "list_connections",
  '/api/connection/kill/', "kill_connection",
)

class list_connections:

    def GET(self):
        users = list_users()
        return json.dumps(users, indent=2)

class kill_connection:

    def POST(self):
        user_data = web.input()
        ok = kick_user(conn_id=user_data.get('conn_id'), virtual_ip=user_data.get('virtual_ip'))
        return json.dumps({'ok' : ok, 'request' : user_data}, indent=2)

app = web.application(urls, globals())

application = app.wsgifunc()

def main():
    app.run()

if __name__ == "__main__":
    main()
