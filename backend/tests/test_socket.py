"""Socket.IO tests for ECDLP solver events.

Tests cover:
- Successful solve via socket (small curve)
- Invalid curve_id error
- Task cancellation on general_40bit (slow)
- Missing fields error

Run:
    cd backend
    python -m pytest tests/test_socket.py -v
"""

import threading
import time
import pytest

import socketio
import uvicorn

from api.main import app

class SocketClient:
    """Wraps a socketio.Client with simple sync event capture."""

    def __init__(self, base_url: str):
        self.sio = socketio.Client()
        self.base_url = base_url
        self._events: list[tuple[str, dict]] = []
        self._lock = threading.Lock()
        self._connected = threading.Event()

        self.sio.on("connect")(self._on_connect)
        self.sio.on("task_started")(lambda d: self._record("task_started", d))
        self.sio.on("task_complete")(lambda d: self._record("task_complete", d))

    def _on_connect(self):
        self._connected.set()

    def _record(self, event: str, data: dict):
        with self._lock:
            self._events.append((event, data))

    def connect(self):
        self.sio.connect(self.base_url, socketio_path="/ws")
        self._connected.wait(timeout=5)
        assert self._connected.is_set(), "Socket.IO connection timed out"

    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect()

    def emit(self, event: str, data: dict):
        self.sio.emit(event, data)

    def wait_for_event(self, event_name: str, timeout: float = 30) -> dict | None:
        """Blocks until an event with the given name is received, or timeout."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                for i, (name, data) in enumerate(self._events):
                    if name == event_name:
                        self._events.pop(i)
                        return data
            time.sleep(0.2)
        return None

    def clear_events(self):
        with self._lock:
            self._events.clear()


@pytest.fixture(scope="module")
def server():
    """Starts the FastAPI+Socket.IO server on a random port in a background thread."""
    import socket
    import requests

    # Find a free port
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    def run():
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

    base_url = f"http://127.0.0.1:{port}"

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    start_time = time.time()
    server_ready = False

    while time.time() - start_time < 5:
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                server_ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    
    if not server_ready:
        pytest.fail("Server failed to start within 5 seconds")

    yield base_url

    # Shutdown is automatic (daemon thread), but be polite
    time.sleep(0.5)


@pytest.fixture
def client(server):
    """Creates a Socket.IO client, connects, yields, then disconnects."""
    c = SocketClient(server)
    c.connect()
    yield c
    c.disconnect()


# ---------------------------------------------------------------------------
# Socket.IO tests
# ---------------------------------------------------------------------------

class TestSocketSolve:
    def test_solve_small_curve_returns_result(self, server, client):
        """Solve a fast curve and verify task_started + task_complete with result."""
        x = "0xab"
        client.emit("solve", {"curve_id": "general_16bit_0", "x": x})

        started = client.wait_for_event("task_started", timeout=5)
        assert started is not None
        assert "task_id" in started

        complete = client.wait_for_event("task_complete", timeout=30)
        assert complete is not None
        assert complete["status"] == "completed"
        assert complete["result"] == x

    def test_solve_invalid_curve_returns_error(self, server, client):
        x = "0xabcd"
        client.emit("solve", {"curve_id": "nonexistent", "x": x})

        complete = client.wait_for_event("task_complete", timeout=5)
        assert complete is not None
        assert complete["status"] == "failed"
        assert "not found" in complete["error"]

    def test_solve_missing_fields_returns_error(self, server, client):
        client.emit("solve", {})

        complete = client.wait_for_event("task_complete", timeout=5)
        assert complete is not None
        assert complete["status"] == "failed"
        assert "Missing" in complete["error"]


class TestSocketCancel:
    def test_cancel_on_slow_curve(self, server, client):
        """Start solve on general_40bit (slow), cancel it, verify cancelled status."""
        x = "0xffffffff"
        client.emit("solve", {"curve_id": "general_40bit_0", "x": x})

        started = client.wait_for_event("task_started", timeout=5)
        assert started is not None
        task_id = started["task_id"]

        # Cancel immediately
        client.emit("cancel", {"task_id": task_id})

        complete = client.wait_for_event("task_complete", timeout=10)
        assert complete is not None
        assert complete["status"] == "cancelled"
        assert complete["task_id"] == task_id

    def test_cancel_nonexistent_task(self, server, client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        client.emit("cancel", {"task_id": fake_id})

        complete = client.wait_for_event("task_complete", timeout=5)
        assert complete is not None
        assert complete["status"] == "failed"
        assert complete["task_id"] == fake_id

    def test_cancel_missing_task_id_field(self, server, client):
        client.emit("cancel", {})

        complete = client.wait_for_event("task_complete", timeout=5)
        assert complete is not None
        assert complete["status"] == "failed"
        assert "Missing" in complete["error"]
