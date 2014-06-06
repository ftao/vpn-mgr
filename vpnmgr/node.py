import zmq

class Node(object):
    def __init__(self, socket):
        self._socket = socket

    def poll(self, timeout):
        socket = self._socket
        events = socket.poll(timeout=timeout, flags=zmq.POLLIN)
        if events != 0:
            return socket.recv_multipart()
        else:
            return None

    def send(self, msg):
        self._socket.send_multipart(msg)
