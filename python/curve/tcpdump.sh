#!/bin/bash
# Run tcpdump to get zmq packets and see what is happening
# Based on: http://lists.zeromq.org/pipermail/zeromq-dev/2013-March/020824.html
# tested with:
# * tcpdump version 4.6.2
# * libpcap version 1.6.2
# * OpenSSL 1.0.1j 15 Oct 2014
# * SMI-library: 0.4.8

tcpdump -vv -ni lo0 -T zmtp1 tcp port 5555
