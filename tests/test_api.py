"""
Integration tests untuk API
"""

import pytest
import json
import sys
import os
from pathlib import Path
import subprocess
import time
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = "http://localhost:5000/api"
API_TIMEOUT = 5


@pytest.fixture(scope="session", autouse=True)
def start_api_server():
    """Start Flask API server untuk testing"""
    # Try to start the server
    try:
        # Check if server is already running
        requests.get(f"{API_URL}/status", timeout=2)
        yield
        return
    except:
        # Start server in background
        server_process = subprocess.Popen(
            ["python", "simple_server.py"],
            cwd=str(Path(__file__).parent.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        max_retries = 30
        for i in range(max_retries):
            try:
                requests.get(f"{API_URL}/status", timeout=2)
                break
            except Exception as e:
                time.sleep(1)

        yield

        # Cleanup
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_status_endpoint(self):
        """Test /api/status endpoint"""
        response = requests.get(f"{API_URL}/status", timeout=API_TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "running", "healthy"]

    def test_diagnose_endpoint_exists(self):
        """Test /api/diagnose endpoint ada"""
        response = requests.post(
            f"{API_URL}/diagnose", json={"symptoms": {}}, timeout=API_TIMEOUT
        )
        # Accept 200 atau 400 (bad request)
        assert response.status_code in [200, 400, 422]

    def test_rules_endpoint(self):
        """Test /api/rules endpoint"""
        response = requests.get(f"{API_URL}/rules", timeout=API_TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))


class TestDiagnosisAPI:
    """Test diagnosis API functionality"""

    def test_valid_diagnosis_request(self):
        """Test diagnosis request dengan data valid"""
        payload = {"symptoms": {"fever": {"present": True, "cf": 0.9}}}
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or "diagnosis" in data

    def test_multiple_symptoms_diagnosis(self):
        """Test diagnosis dengan multiple symptoms"""
        payload = {
            "symptoms": {
                "fever": {"present": True, "cf": 0.9},
                "cough": {"present": True, "cf": 0.8},
                "difficulty_breathing": {"present": True, "cf": 0.85},
            }
        }
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data is not None

    def test_empty_symptoms_request(self):
        """Test diagnosis dengan symptoms kosong"""
        payload = {"symptoms": {}}
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )
        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_invalid_cf_values(self):
        """Test diagnosis dengan invalid CF"""
        payload = {"symptoms": {"fever": {"present": True, "cf": 1.5}}}  # CF > 1
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )
        # Should return error
        assert response.status_code in [400, 422]

    def test_diagnosis_response_format(self):
        """Test format response diagnosis"""
        payload = {"symptoms": {"fever": {"present": True, "cf": 0.9}}}
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            # Check response structure
            assert isinstance(data, dict)


class TestAPIErrorHandling:
    """Test API error handling"""

    def test_malformed_json(self):
        """Test request dengan malformed JSON"""
        response = requests.post(
            f"{API_URL}/diagnose",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=API_TIMEOUT,
        )
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self):
        """Test request dengan missing required fields"""
        response = requests.post(
            f"{API_URL}/diagnose", json={}, timeout=API_TIMEOUT  # Missing 'symptoms'
        )
        assert response.status_code in [400, 422]

    def test_nonexistent_endpoint(self):
        """Test request ke endpoint yang tidak ada"""
        response = requests.get(f"{API_URL}/nonexistent-endpoint", timeout=API_TIMEOUT)
        assert response.status_code == 404


class TestAPIPerformance:
    """Test API performance"""

    def test_diagnosis_response_time(self):
        """Test diagnosis response time < 2 detik"""
        payload = {
            "symptoms": {
                "fever": {"present": True, "cf": 0.9},
                "cough": {"present": True, "cf": 0.8},
            }
        }

        import time

        start = time.time()
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Response took {elapsed}s, should be < 2s"

    def test_api_under_load(self):
        """Test API bisa handle multiple concurrent requests"""
        import concurrent.futures

        payload = {"symptoms": {"fever": {"present": True, "cf": 0.9}}}

        def make_request():
            response = requests.post(
                f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
            )
            return response.status_code == 200

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, range(10)))

        # Sebagian besar request harus succeed
        assert sum(results) >= 8


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
