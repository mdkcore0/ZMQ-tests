import  zmq
import json
import sys
import os

from random import randint

import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

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

    # certificates
    base_dir = os.path.dirname(__file__)
    public_keys_dir = os.path.join(base_dir, 'public_keys')
    secret_keys_dir = os.path.join(base_dir, 'private_keys')

    # zmq setup
    context = zmq.Context()

    # auth setup
    auth = ThreadAuthenticator(context)
    auth.start()
    auth.allow('127.0.0.1')
    auth.configure_curve(domain='*', location=public_keys_dir)

    # asynchronous =D
    socket = context.socket(zmq.DEALER)

    ident = "banana%s" % randint(0, 100)
    socket.identity = ident.encode("ascii")

    # client auth setup
    client_secret_file = os.path.join(secret_keys_dir, "client.key_secret")
    client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
    socket.curve_secretkey = client_secret
    socket.curve_publickey = client_public

    server_public_file = os.path.join(public_keys_dir, "server.key")
    server_public, _ = zmq.auth.load_certificate(server_public_file)
    socket.curve_serverkey = server_public

    socket.connect("tcp://localhost:5555")

    print "I am '%s' client" % ident

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

    auth.stop()
    socket.close()
    context.term()
