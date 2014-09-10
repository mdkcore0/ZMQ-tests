import zmq
import time
import json
import sys

# dict test data
dictTest = {
        '0': {'name': 'Zoiao', 'id': 23},
        '1': {'name': 'Ratao', 'id': 69}}

# json test data
jsonTest = [
        {'name': 'Zoiao', 'id': 23},
        {'name': 'Ratao', 'id': 69}]

if __name__ == '__main__':
    # argument validation
    if len(sys.argv) < 2:
        print "Thou shalt run as: %s [json | dict]" % sys.argv[0]
        sys.exit()

    use_json = False
    use_dict = False

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
    socket = context.socket(zmq.REP)

    socket.bind("tcp://*:5555")

    # run baby, run
    while True:
        message = socket.recv()
        print message

        time.sleep(1)

        if use_json:
            socket.send_json(jsonTest)
        else:
            socket.send_pyobj(dictTest)
