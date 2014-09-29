import zmq
import time
import json
import sys

from threading import Thread

import utils

jsonData = [
        {'name': 'Zoiao', 'id': 23},
        {'name': 'Ratao', 'id': 69}
        ]

class Worker(Thread):
    def __init__(self, context):
        Thread.__init__(self)

        self.context = context

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect("inproc://backend")

        print "Server worker thread started"

        while True:
            ident, message = worker.recv_multipart()
            message = json.loads(message)

            utils.log("<<", ident, message)

            reply_message = ""
            if message["type"] == "message" and message["data"] == "Yo!":
                reply_message = {'type': 'list', 'data': jsonData}
            if message["type"] == "message" and message["data"] == "PING":
                reply_message = {'type': 'message', 'data': 'PONG'}

            worker.send(ident, zmq.SNDMORE)
            worker.send_json(reply_message)

            utils.log(">>", ident, reply_message)

            # a little wait to avoid chaos :p
            time.sleep(1.0)

        worker.close()

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

    # TODO disconnection
    clients = []

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

                    worker = Worker(context)
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
