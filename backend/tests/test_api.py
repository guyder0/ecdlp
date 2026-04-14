"""REST API tests for ECDLP solver endpoints.

Tests cover:
- Curve listing and detail
- Solve task creation (valid / invalid curve_id)
- Task status polling
- Task cancellation (on general_40bit which is slow)

Run:
    cd backend
    python -m pytest tests/test_api.py -v
"""

import time
import pytest
from starlette.testclient import TestClient

from api.main import app
from api.curves import CURVE_REGISTRY


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Curve listing
# ---------------------------------------------------------------------------

class TestListCurves:
    def test_list_curves_returns_list(self, client):
        resp = client.get("/api/v1/curves")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == len(CURVE_REGISTRY)

    def test_list_curves_items_have_required_fields(self, client):
        resp = client.get("/api/v1/curves")
        assert resp.status_code == 200
        for item in resp.json():
            assert set(item.keys()) >= {"id", "name", "description"}

    def test_all_registry_keys_are_in_response(self, client):
        resp = client.get("/api/v1/curves")
        ids = {item["id"] for item in resp.json()}
        assert ids == set(CURVE_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Curve detail
# ---------------------------------------------------------------------------

class TestGetCurve:
    def test_get_existing_curve(self, client):
        key = "general_16bit_0"
        resp = client.get(f"/api/v1/curves/{key}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == key
        assert "p" in data
        assert "q" in data
        assert "gx" in data
        assert "gy" in data

    def test_get_nonexistent_curve_returns_404(self, client):
        resp = client.get("/api/v1/curves/does_not_exist")
        assert resp.status_code == 404

    def test_get_curve_matches_registry(self, client):
        key = "anomalous_128bit_0"
        resp = client.get(f"/api/v1/curves/{key}")
        data = resp.json()
        entry = CURVE_REGISTRY[key]
        assert data["p"] == entry["p"]
        assert data["a"] == entry["a"]
        assert data["b"] == entry["b"]
        assert data["q"] == entry["q"]
        assert data["gx"] == entry["gx"]
        assert data["gy"] == entry["gy"]


# ---------------------------------------------------------------------------
# Solve task creation
# ---------------------------------------------------------------------------

class TestSolve:
    def test_solve_invalid_curve_id_returns_400(self, client):
        resp = client.post(
            "/api/v1/solve",
            json={"curve_id": "nonexistent", "x": 123},
        )
        assert resp.status_code == 400

    def test_solve_creates_task_and_returns_202(self, client):
        resp = client.post(
            "/api/v1/solve",
            json={"curve_id": "general_16bit_0", "x": 42},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert "task_id" in data
        # Small curves may already be completed by response time
        assert data["status"] in ("pending", "running", "completed")

    @pytest.mark.parametrize("curve_id", [
        "general_16bit_0",
        "general_32bit_0",
    ])
    def test_solve_small_curve_returns_correct_result(self, client, curve_id):
        """Solve a small curve and verify the result."""
        x = 99
        resp = client.post(
            "/api/v1/solve",
            json={"curve_id": curve_id, "x": x},
        )
        assert resp.status_code == 202
        task_id = resp.json()["task_id"]

        # Poll until completed (with timeout)
        for _ in range(60):
            time.sleep(0.5)
            t_resp = client.get(f"/api/v1/tasks/{task_id}")
            task = t_resp.json()
            if task["status"] in ("completed", "failed"):
                break

        assert task["status"] == "completed"
        assert task["result"] == x

    def test_solve_missing_fields_returns_422(self, client):
        resp = client.post("/api/v1/solve", json={})
        assert resp.status_code == 422

    def test_solve_x_must_be_positive(self, client):
        resp = client.post(
            "/api/v1/solve",
            json={"curve_id": "general_16bit_0", "x": 0},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Task cancellation
# ---------------------------------------------------------------------------

class TestCancelTask:
    def test_cancel_nonexistent_task_returns_404(self, client):
        resp = client.post("/api/v1/tasks/00000000-0000-0000-0000-000000000000/cancel")
        assert resp.status_code == 404

    def test_cancel_on_slow_curve_returns_cancelled_status(self, client):
        """Start a solve on general_40bit (slow), cancel it, verify status."""
        x = 1_000_000_007  # large secret to ensure it takes time
        resp = client.post(
            "/api/v1/solve",
            json={"curve_id": "general_40bit_0", "x": x},
        )
        assert resp.status_code == 202
        task_id = resp.json()["task_id"]

        # Cancel immediately
        c_resp = client.post(f"/api/v1/tasks/{task_id}/cancel")
        assert c_resp.status_code == 200

        # Poll until cancellation propagates
        for _ in range(30):
            time.sleep(0.5)
            t_resp = client.get(f"/api/v1/tasks/{task_id}")
            task = t_resp.json()
            if task["status"] == "cancelled":
                break

        assert task["status"] == "cancelled"
        assert task["curve_id"] == "general_40bit_0"
