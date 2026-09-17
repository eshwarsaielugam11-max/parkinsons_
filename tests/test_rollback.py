import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.config import settings

@pytest.fixture
def client():
    return TestClient(app)

def test_versioned_rollout_and_rollback_simulation(client):
    """
    Simulates production version rollout and immediate rollback:
    1. Baseline Release v1.0.0: /health serves model_v1.0.0
    2. Upgrade Rollout v1.1.0: /health serves model_v1.1.0
    3. Emergency Rollback to v1.0.0: /health reverts to model_v1.0.0 with healthy DB & vector DB connectivity
    """
    # 1. Initial State: v1.0.0
    with patch.object(settings, "MODEL_VERSION", "model_v1.0.0"):
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["model_version"] == "model_v1.0.0"
        assert data["status"] in ["healthy", "ok"]
        assert data["services"]["database"] == "connected"

    # 2. Upgrade Rollout Simulation: v1.1.0
    with patch.object(settings, "MODEL_VERSION", "model_v1.1.0"):
        res_upgraded = client.get("/api/v1/health")
        assert res_upgraded.status_code == 200
        data_upgraded = res_upgraded.json()
        assert data_upgraded["model_version"] == "model_v1.1.0"
        assert data_upgraded["status"] in ["healthy", "ok"]

    # 3. Emergency Rollback Simulation back to: v1.0.0
    with patch.object(settings, "MODEL_VERSION", "model_v1.0.0"):
        res_rollback = client.get("/api/v1/health")
        assert res_rollback.status_code == 200
        data_rollback = res_rollback.json()
        assert data_rollback["model_version"] == "model_v1.0.0"
        assert data_rollback["services"]["database"] == "connected"
        assert data_rollback["services"]["vector_db"] == "connected"
