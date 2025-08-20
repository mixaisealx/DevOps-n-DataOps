import os
import random
from contextlib import closing

import pytest
from testable_thread import TestableThread

from protocol import MyTCPProtocol
from servers import EchoClient, EchoServer, ParallelClientServer

allocated_ports = {}


def allocate_port():
    while True:
        port = random.randrange(20000, 40000)
        if port not in allocated_ports:
            break
    allocated_ports[port] = True
    return port


def execute_test_scenario(client_class, server_class, iterations, msg_size=None):
    client_addr = ('127.0.0.1', allocate_port())
    server_addr = ('127.0.0.1', allocate_port())

    with closing(MyTCPProtocol(local_addr=client_addr, remote_addr=server_addr)) as client_protocol, \
         closing(MyTCPProtocol(local_addr=server_addr, remote_addr=client_addr)) as server_protocol:

        client = client_class(client_protocol, iterations=iterations, msg_size=msg_size)
        server = server_class(server_protocol, iterations=iterations, msg_size=msg_size)

        client_thread = TestableThread(target=client.run)
        server_thread = TestableThread(target=server.run)
        client_thread.daemon = True
        server_thread.daemon = True

        client_thread.start()
        server_thread.start()

        client_thread.join()
        server_thread.join()


active_netem_config = None


def configure_netem(packet_loss, duplicate, reorder):
    global active_netem_config
    if active_netem_config == (packet_loss, duplicate, reorder):
        return
    active_netem_config = (packet_loss, duplicate, reorder)
    netem_cmd = f"tc qdisc replace dev lo root netem loss {packet_loss * 100}% duplicate {duplicate * 100}%"
    if reorder > 0.0001:
        netem_cmd += f" reorder {reorder * 100}%"
    netem_cmd += " delay 10ms rate 1Mbit"
    os.system(netem_cmd)


@pytest.mark.parametrize("iterations", [10, 50, 100])
@pytest.mark.timeout(30)
def test_basic(iterations):
    configure_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    execute_test_scenario(EchoClient, EchoServer, iterations=iterations, msg_size=11)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_small_loss(iterations):
    configure_netem(packet_loss=0.02, duplicate=0.0, reorder=0.0)
    execute_test_scenario(EchoClient, EchoServer, iterations=iterations, msg_size=14)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_small_duplicate(iterations):
    configure_netem(packet_loss=0.0, duplicate=0.02, reorder=0.0)
    execute_test_scenario(EchoClient, EchoServer, iterations=iterations, msg_size=14)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_high_loss(iterations):
    configure_netem(packet_loss=0.1, duplicate=0.0, reorder=0.0)
    execute_test_scenario(EchoClient, EchoServer, iterations=iterations, msg_size=17)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(30)
def test_high_duplicate(iterations):
    configure_netem(packet_loss=0.0, duplicate=0.1, reorder=0.0)
    execute_test_scenario(EchoClient, EchoServer, iterations=iterations, msg_size=14)


@pytest.mark.parametrize("msg_size", [100, 100_000, 5_000_000])
@pytest.mark.timeout(180)
def test_large_message(msg_size):
    configure_netem(packet_loss=0.02, duplicate=0.02, reorder=0.9999)
    execute_test_scenario(EchoClient, EchoServer, iterations=2, msg_size=msg_size)

@pytest.mark.parametrize("iterations", [10, 100, 500])
@pytest.mark.timeout(20)
def test_parallel(iterations):
    configure_netem(packet_loss=0.0, duplicate=0.0, reorder=0.0)
    execute_test_scenario(ParallelClientServer, ParallelClientServer, iterations=iterations)

@pytest.mark.parametrize("iterations", [50_000])
@pytest.mark.timeout(60)
def test_performance(iterations):
    configure_netem(packet_loss=0.02, duplicate=0.02, reorder=0.9999)
    execute_test_scenario(EchoClient, EchoServer, iterations=iterations, msg_size=10)
