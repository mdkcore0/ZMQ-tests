#include <zmq.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main(int argc, char **argv) {
    void *context = zmq_ctx_new();
    void *socket = zmq_socket(context, ZMQ_REQ);

    zmq_connect(socket, "tcp://localhost:5555");

    int request_nbr;
    for (request_nbr = 0; request_nbr != 10; request_nbr++) {
        char buffer[10];

        printf("Sending Hey %d...\n", request_nbr);

        zmq_send(socket, "Hey", 3, 0);
        zmq_recv(socket, buffer, 10, 0);

        printf("Received Yo %d\n", request_nbr);
    }

    zmq_close(socket);
    zmq_ctx_destroy(context);

    return 0;
}
