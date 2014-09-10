import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REP)

socket.bind("tcp://*:5555")

while True:
    message = socket.recv()
    print "Received Hey"

    time.sleep(1)

    socket.send(b"Yo")
