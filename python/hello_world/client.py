import  zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)

socket.connect("tcp://localhost:5555")

for request_nbr in xrange(10):
    print "Sending Hey %s..." % request_nbr
    socket.send(b"Hey")

    message = socket.recv()
    print "Received Yo %s" % request_nbr
