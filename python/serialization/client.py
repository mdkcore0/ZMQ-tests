import  zmq
import json
import sys

if __name__ == '__main__':
    # argument validation
    if len(sys.argv) < 2:
        print "Thou shalt run as: %s [json | dict]" % sys.argv[0]
        sys.exit()

    use_json = False
    use_dict = False

    if sys.argv[1] == 'json':
        print "Receiving data as json"
        use_json = True
    elif sys.argv[1] == 'dict':
        print "Receiving data as dict"
        use_dict = True
    else:
        print "Unknown argument: %s" % sys.argv[1]
        sys.exit()

    # zmq setup
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    socket.connect("tcp://localhost:5555")

    # run baby, run
    socket.send("Yo!")

    if use_json:
        message = socket.recv_json()
        print "Number of items: %s" % len(message)
        print "'Raw' message: %s" % message

        print "json indented data:"
        print json.dumps(message, indent=4)

        print "Message data:"
        for item in message:
            #if 'name' in item:
            print "Name: %s | Id: %s" % (item['name'], item['id'])
    else:
        message = socket.recv_pyobj()
        print "Number of items: %s" % len(message)
        print "'Raw' message: %s" % message

        print "Message data:"
        for key in message:
            #if 'name' in message[i]:
            print "Name: %s | Id: %s" % (message[key]['name'],
                    message[key]['id'])
