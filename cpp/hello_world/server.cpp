#include <zmq.hpp>
#include <string>
#include <iostream>
#include <unistd.h>

using namespace std;

int main(int argc, char **argv) {
    zmq::context_t context(1);
    zmq::socket_t socket(context, ZMQ_REP);

    socket.bind("tcp://*:5555");

    while (true) {
        zmq::message_t request;

        socket.recv(&request);
        cout << "Received Hey" << endl;

        sleep(1);

        zmq::message_t reply(5);

        memcpy((void *)reply.data(), "Yo", 2);
        socket.send(reply);
    }

    return 0;
}
