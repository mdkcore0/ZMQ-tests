#include <zmq.hpp>
#include <string>
#include <iostream>

using namespace std;

int main(int argc, char **argv) {
    zmq::context_t context(1);
    zmq::socket_t socket(context, ZMQ_REQ);

    socket.connect("tcp://localhost:5555");

    int request_nbr;
    for (request_nbr = 0; request_nbr != 10; request_nbr++) {
        zmq::message_t request(6);

        memcpy((void *)request.data(), "Hey", 3);

        cout << "Sending Hey " << request_nbr << "..." << endl;
        socket.send(request);

        zmq::message_t reply;
        socket.recv(&reply);
        cout << "Received Yo " << request_nbr << endl;
    }

    return 0;
}
