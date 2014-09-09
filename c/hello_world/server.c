#include <zmq.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>

int main(int argc, char **argv) {
    void *context = zmq_ctx_new();
    void *socket = zmq_socket(context, ZMQ_REP);

    int rc = zmq_bind(socket, "tcp://*:5555");
    assert(rc == 0);

    while (1) {
        char buffer[10];

        zmq_recv(socket, buffer, 10, 0);

        printf("Received Hey\n");
        sleep(1);

        zmq_send(socket, "Yo", 2, 0);
    }

    return 0;
}
