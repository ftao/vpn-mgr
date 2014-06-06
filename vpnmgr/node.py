import logging
import zmq

class Node(object):
    poll_interval = 1000

    def __init__(self, nid, socket):
        self.nid = nid
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

    def run(self):
        while True:
            msg = self.poll(self.poll_interval)
            if msg is None:
                try:
                    self.handle_idle()
                except:
                    logging.exception("error handle idle")
            else:
                try:
                    self.handle_msg(msg)
                except:
                    logging.exception("error handle msg")

    def handle_idle(self):
        pass

    def handle_msg(self, msg):
        pass

