#!/usr/bin/env python
'''OpenVPN'''
import fdpexpect
import logging
import socket

logger = logging.getLogger()

class OpenVPNServer(object):
    '''OpenVPN Serve
    >>> import mock
    >>> data = """OpenVPN CLIENT LIST
    ... Updated,Wed Aug 14 13:21:07 2013
    ... Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
    ... demo,222.65.164.43:19542,7666,9983,Wed Aug 14 13:19:13 2013
    ... ROUTING TABLE
    ... Virtual Address,Common Name,Real Address,Last Ref
    ... 10.8.1.6,demo,222.65.164.43:19542,Wed Aug 14 13:19:47 2013
    ... GLOBAL STATS
    ... Max bcast/mcast queue length,0"""
    >>> @mock.patch.object(OpenVPNServer, '_connect', lambda x,y: y)
    ... @mock.patch.object(OpenVPNServer, '_get_status_text', lambda x,fd:data)
    ... def test_list_user():
    ...     print OpenVPNServer('tcp://127.0.0.1:9900').list_users()
    >>> test_list_user()
    [{'username': 'demo', 'tx': 9983, 'local_ip': '10.8.1.6', 'rx': 7666, 'time': 'Wed Aug 14 13:19:13 2013', 'remote_ip': '222.65.164.43'}]
    '''

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def list_users(self):
        sock = self._connect(self.endpoint)
        if sock:
            return self._list_users(sock)
        else:
            return []

    def kick_user(self, username):
        sock = self._connect(self.endpoint)
        if sock:
            return self._kick_user(sock, username)
        else:
            return False

    def _connect(self, endpoint):
        sock = None
        if endpoint.startswith('tcp://'):
            host,port = endpoint[6:].split(':', 1)
            port = int(port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        elif endpoint.startswith('unix://'):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(endpoint[7:])
        return sock

    def _get_status_text(self, fd):
        child = fdpexpect.fdspawn(fd)
        child.expect('>INFO:OpenVPN')
        child.sendline('status')
        child.expect('END')
        data = child.before.strip()
        child.sendline('exit')
        child.close()
        return data

    def _list_users(self, fd):
        data = self._get_status_text(fd)

        users = []
        for client in self._parse_status_output(data):
            users.append({
                'username' : client['cname'],
                'time' : client['since'],
                'local_ip' : client['virtual_address'],
                'remote_ip': client['real_address'].split(':')[0],
                'tx' : client['tx'],
                'rx' : client['rx'],
            })
        return users

    @staticmethod
    def _parse_status_output(text):
        '''
        >>> data = """OpenVPN CLIENT LIST
        ... Updated,Wed Aug 14 13:21:07 2013
        ... Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
        ... demo,222.65.164.43:19542,7666,9983,Wed Aug 14 13:19:13 2013
        ... ROUTING TABLE
        ... Virtual Address,Common Name,Real Address,Last Ref
        ... 10.8.1.6,demo,222.65.164.43:19542,Wed Aug 14 13:19:47 2013
        ... GLOBAL STATS
        ... Max bcast/mcast queue length,0"""
        >>> users = OpenVPNServer._parse_status_output(data)
        >>> len(users)
        1
        >>> users[0]['cname']
        'demo'
        >>> users[0]['virtual_address']
        '10.8.1.6'
        >>> users[0]['real_address']
        '222.65.164.43:19542'
        >>> users[0]['rx']
        7666
        >>> users[0]['tx']
        9983
        '''
        clients_text, routing_text = text.split("ROUTING TABLE")
        clients = []
        for line in clients_text.strip().split('\n')[::-1]:
            if line.startswith('Common Name'):
                break
            cname,real_address,rx,tx,since = line.strip().split(',') 
            clients.append({"cname" : cname, "real_address" : real_address, "rx" : int(rx), "tx" : int(tx), "since" : since})

        routing_text = routing_text.split("GLOBAL STATS")[0].strip()
        for line in routing_text.split('\n')[::-1]:
            if line.startswith('Virtual Address'):
                break
            virtual_address,cname,real_address,last_ref = line.strip().split(',') 
            for client in clients:
                if client['cname'] == cname:
                    client["virtual_address"] = virtual_address
                    client["last_ref"] = last_ref
                    break
        return clients

    def _kick_user(self, fd, cname):
        child = fdpexpect.fdspawn(fd)
        child.expect('>INFO:OpenVPN')
        child.sendline('kill %s' %cname)
        index = child.expect(['SUCCESS', 'ERROR'])
        child.sendline('exit')
        child.close()
        return index == 0