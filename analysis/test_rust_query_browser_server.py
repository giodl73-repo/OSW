"""Real loopback socket checks, with no browser or fixed user port."""
import os
import socket
import pytest
from run_rust_query_browser_checks import check_port_available


def test_existing_listener_is_rejected_without_being_stopped():
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', 0)); server.listen()
        address=server.getsockname()
        with pytest.raises(OSError): check_port_available(address)
        # The same listener remains open; the probe has not replaced it.
        assert server.getsockname()==address


@pytest.mark.skipif(os.name=='nt',reason='POSIX TIME_WAIT reuse regression; Windows policy unchanged')
def test_closed_server_time_wait_allows_next_sequential_stage():
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1',0)); server.listen()
        address=server.getsockname()
        with socket.create_connection(address,timeout=2) as client:
            connection,_=server.accept()
            with connection:
                connection.shutdown(socket.SHUT_WR)
                assert client.recv(1)==b''
    check_port_available(address)
