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

MAX_LIVENESS = 3
INTERVAL = 1000.0 * 1 # should be the same of the client
NETWORK_TIME = 10.0 # value from outer world, find a proper value

class Worker(Thread):
    connectionCloseCallback = None

    def __init__(self, context, ident, connectionCloseCallback=None):
        Thread.__init__(self)

        self.context = context

        self.worker = self.context.socket(zmq.DEALER)
        self.worker.setsockopt(zmq.IDENTITY, ident)
        self.worker.connect("ipc://backend")

        self.connectionCloseCallback = connectionCloseCallback

        self.last_ping = 0
        self.liveness = MAX_LIVENESS

        self.setName("thread-%s" % ident)

    def run(self):
        print "Server worker thread started"

        running = True
        while running:
            try:
                ident, message = self.worker.recv_multipart(zmq.NOBLOCK)
                message = json.loads(message)

                utils.log("<<", ident, message, self.name)
                #utils.log("<<", ident, message)

                reply_message = ""
                if message["type"] == "message" and message["data"] == "Yo!":
                    reply_message = utils.create_message('list', jsonData)

                if message["type"] == "message" and message["data"] == "PING":
                    reply_message = utils.create_message('message', 'PONG')

                # assuming any message is a heartbeat
                # XXX change client to send real PINGS only when idle
                self.liveness = MAX_LIVENESS
                self.last_ping = time.time() * 1000.0

                if reply_message:
                    self.worker.send(ident, zmq.SNDMORE)
                    self.worker.send_json(reply_message)

                    #utils.log(">>", ident, reply_message)
            except zmq.ZMQError, e:
                if e.errno == zmq.EAGAIN:
                    if self.last_ping != 0:
                        # maximum accepting time diff
                        accepting = (INTERVAL * (MAX_LIVENESS - self.liveness
                            + 1)) + NETWORK_TIME
                        ping_now = time.time() * 1000.0

                        if ping_now - self.last_ping > accepting:
                            self.liveness -= 1
                            utils.log("--", ident, "no data received (%s/%s)"
                                    % (MAX_LIVENESS - self.liveness,
                                        MAX_LIVENESS))

                            if self.liveness <= 0:
                                utils.log("__", ident, "closing connection")
                                running = False
                else:
                    raise

        self.worker.close()

        if self.connectionCloseCallback:
            self.connectionCloseCallback(ident)

clients = []
def onConnectionClose(ident):
    clients.remove(ident)
    print "Worker '%s' terminated" % ident

if __name__ == '__main__':
    print "Initializing server on port 5555"

    # zmq setup
    context = zmq.Context()
    # will accept incoming connections
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5555")
    # will connect to the worker threads
    backend = context.socket(zmq.DEALER)
    backend.bind("ipc://backend")

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
