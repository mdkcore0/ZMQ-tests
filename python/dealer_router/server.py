import zmq
import time
import json
import sys

from threading import Thread

# dict test data
dictTest = {
        '0': {'name': 'Zoiao', 'id': 23},
        '1': {'name': 'Ratao', 'id': 69}}

# json test data
jsonTest = [
        {'name': 'Zoiao', 'id': 23},
        {'name': 'Ratao', 'id': 69}]

use_json = False
use_dict = False

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
            print "Received a message from client: %s" % ident
            print "\t: %s" % message

            worker.send(ident, zmq.SNDMORE)

            if use_json:
                worker.send_json(jsonTest)
            else:
                worker.send_pyobj(dictTest)

        worker.close()

if __name__ == '__main__':
    # argument validation
    if len(sys.argv) < 2:
        print "Thou shalt run as: %s [json | dict]" % sys.argv[0]
        sys.exit()

    if sys.argv[1] == 'json':
        print "Sending data as json"
        use_json = True
    elif sys.argv[1] == 'dict':
        print "Sending data as dict"
        use_dict = True
    else:
        print "Unknown argument: %s" % sys.argv[1]
        sys.exit()

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

    clients = []

    # will be handled on another example (possible 'ioloop'):
    # heartbeat, multiple clients, disconnection, worker cleanup

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
            print "exiting like a sir"
            running = False
            #sys.exit()

    frontend.close()
    backend.close()
    context.term()
