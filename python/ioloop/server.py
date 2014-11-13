import zmq
import time
import json
import sys

from threading import Thread
from threading import current_thread

import utils

jsonData = [
        {'name': 'Zoiao', 'id': 23},
        {'name': 'Ratao', 'id': 69}
        ]

class Worker(Thread):
    connectionCloseCallback = None

    def __init__(self, context, ident, connectionCloseCallback=None):
    #def __init__(self, context, ident):
        Thread.__init__(self)

        self.context = context

        self.worker = self.context.socket(zmq.DEALER)
        self.worker.setsockopt(zmq.IDENTITY, ident)
        self.worker.connect("inproc://backend")

        self.connectionCloseCallback = connectionCloseCallback

        self.last_ping = 0
        self.liveness = 3 # TODO

    def run(self):
        print "Server worker thread started"

        running = True
        while running:
            try:
                ident, message = self.worker.recv_multipart(zmq.NOBLOCK)
                message = json.loads(message)

                utils.log("<<", ident, message)

                reply_message = ""
                if message["type"] == "message" and message["data"] == "Yo!":
                    reply_message = utils.create_message('list',
                            jsonData)

                # XXX simple heartbeat, not working yet
                if message["type"] == "message" and message["data"] == "PING":
                    reply_message = utils.create_message('message', 'PONG')

                # any message is a heartbeat
                # XXX change client to send real PINGS only when idle
                self.liveness = 3 # TODO add a const with the max_liveness
                self.last_ping = time.time() * 1000.0

                self.worker.send(ident, zmq.SNDMORE)
                self.worker.send_json(reply_message)

                utils.log(">>", ident, reply_message)
            except zmq.ZMQError, e:
                if e.errno == zmq.EAGAIN:
                    # test if already received a message
                    if self.last_ping == 0:
                        pass

                    # TIMEOUT + NETWORK TIME
                    accepting = 1000.0 + 10.0 # XXX find network time :p
                    ping_now = time.time() * 1000.0

                    print "%s %s | %s" % (ping_now, accepting, ping_now - self.last_ping)
                    if ping_now - self.last_ping > accepting:
                        self.liveness -= 1
                        print "te liga: %s" % self.liveness

                        if self.liveness <= 0:
                            print "FOI-SE: %s" % self.liveness
                            running = False

                    # a little wait to avoid chaos :p
                    time.sleep(1.0)
                else:
                    raise

        self.worker.close()

        if self.connectionCloseCallback:
            self.connectionCloseCallback(ident)

# TODO disconnection
clients = []
def onConnectionClose(ident):
    print "HEY, '%s' TERMINATED!" % ident
    clients.remove(ident)

if __name__ == '__main__':
    print "Initializing server on port 5555"

    # zmq setup
    context = zmq.Context()
    # will accept incoming connections
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5555")
    # will connect to the worker threads
    backend = context.socket(zmq.DEALER)
    backend.bind("inproc://backend")

    # pool sockets for activity
    poll = zmq.Poller()
    poll.register(frontend, zmq.POLLIN)
    poll.register(backend,  zmq.POLLIN)

    # run baby, run
    running = True
    while running:
        try:
            sockets = dict(poll.poll())

            # received a message from some client
            if frontend in sockets:
                ident, message = frontend.recv_multipart()

                if ident not in clients:
                    clients.append(ident)

                    worker = Worker(context, ident, onConnectionClose)
                    #worker = Worker(context, ident)
                    worker.start()

                backend.send_multipart([ident, message])

            # received a message from some worker thread
            if backend in sockets:
                ident, message = backend.recv_multipart()
                frontend.send_multipart([ident, message])
        except KeyboardInterrupt:
            print "Exiting like a sir"
            running = False

    frontend.close()
    backend.close()
    context.term()
