import zmq
import json
import sys

from zmq.eventloop.ioloop import ZMQIOLoop
from zmq.eventloop.ioloop import PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

from random import randint

import utils

socket = None
ident = ""

def heartbeat():
    try:
        message = utils.create_message('message', 'PING')
        socket.send_json(message)

        utils.log(">>", ident, message)
    except Exception as e:
        print "Heartbeat error %s" % e.message
        loop.stop()

def handle_recv(msg):
    message = json.loads(msg[0])

    append = ""
    if message["type"] == "list":
        append = "some data arrived"
    if message["type"] == "message" and message["data"] == "PONG":
        append = "SERVER IS ON!"

    utils.log("<<", ident, message, append)

if __name__ == '__main__':
    ident = "banana%s" % randint(0, 100)
    print "I am '%s' client" % ident

    # zmq setup
    context = zmq.Context()

    # asynchronous =D
    socket = context.socket(zmq.DEALER)

    loop = ZMQIOLoop.instance()

    socket.identity = ident.encode("ascii")
    socket.connect("tcp://localhost:5555")

    # we can use 'socket' instead os 'socket_stream' as well
    socket_stream = ZMQStream(socket, loop)
    socket_stream.on_recv(handle_recv)

    # run baby, run
    message = utils.create_message('message', 'Yo!')
    socket.send_json(message)

    utils.log(">>", ident, message)

    pc = PeriodicCallback(heartbeat, 1000, loop)
    pc.start()

    try:
        loop.start()
    except KeyboardInterrupt:
        print "Exiting like a sir"

    loop.stop()
    socket.close()
    context.term()
