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
    server_process = None
    server_log_stdout = None
    server_log_stderr = None

    try:
        # Check if server is already running
        try:
            resp = requests.get(f"{API_URL}/status", timeout=2)
            if resp.status_code == 200:
                print("\n✅ API server already running on port 5000")
                yield
                return
        except Exception:
            pass

        # Start server in background with proper error handling
        print(f"\n🚀 Starting API server from {Path(__file__).parent.parent}...")

        # Create log files to capture server output
        import tempfile

        log_dir = tempfile.gettempdir()
        if os.path.exists(log_dir):
            server_log_stdout = open(
                os.path.join(log_dir, "sispak_server_stdout.log"), "w"
            )
            server_log_stderr = open(
                os.path.join(log_dir, "sispak_server_stderr.log"), "w"
            )

        try:
            # Use Python explicitly to run the server
            import sys as sys_module

            python_path = sys_module.executable

            server_process = subprocess.Popen(
                [python_path, "simple_server.py"],
                cwd=str(Path(__file__).parent.parent),
                stdout=server_log_stdout or subprocess.PIPE,
                stderr=server_log_stderr or subprocess.PIPE,
                preexec_fn=None,  # Required for proper subprocess handling
            )

            print(f"📋 Server process started with PID {server_process.pid}")

            # Wait for server to start with better diagnostics
            max_retries = 40  # Increased from 30
            server_started = False
            last_error = None

            for attempt in range(max_retries):
                try:
                    resp = requests.get(f"{API_URL}/status", timeout=2)
                    if resp.status_code == 200:
                        print(
                            f"✅ API server ready (attempt {attempt + 1}/{max_retries})"
                        )
                        server_started = True
                        break
                except Exception as e:
                    last_error = str(e)
                    if attempt % 10 == 0:  # Log every 10 attempts
                        print(
                            f"⏳ Waiting for server... (attempt {attempt + 1}/{max_retries})"
                        )
                    time.sleep(1)

            if not server_started:
                # Try to read server output for debugging
                error_msg = f"Failed to start API server after {max_retries} attempts. Last error: {last_error}"
                if server_log_stderr:
                    try:
                        server_log_stderr.flush()
                        with open(server_log_stderr.name) as f:
                            stderr_content = f.read()
                            if stderr_content:
                                error_msg += f"\nServer stderr:\n{stderr_content[:500]}"
                    except Exception:
                        pass

                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg)

            yield

        finally:
            # Cleanup server process
            if server_process:
                print("\n🛑 Terminating API server...")
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                    print("✅ Server terminated gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠️  Server did not terminate, killing...")
                    server_process.kill()
                    server_process.wait()

    finally:
        # Close log files
        if server_log_stdout:
            server_log_stdout.close()
        if server_log_stderr:
            server_log_stderr.close()


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
        payload = {"symptoms": {"demam_tinggi": {"present": True, "cf": 0.9}}}
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
                "demam_tinggi": {"present": True, "cf": 0.9},
                "batuk_kering": {"present": True, "cf": 0.8},
                "sesak_napas": {"present": True, "cf": 0.85},
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
        payload = {"symptoms": {"demam_tinggi": {"present": True, "cf": 1.5}}}  # CF > 1
        response = requests.post(
            f"{API_URL}/diagnose", json=payload, timeout=API_TIMEOUT
        )
        # Should return error
        assert response.status_code in [400, 422]

    def test_diagnosis_response_format(self):
        """Test format response diagnosis"""
        payload = {"symptoms": {"demam_tinggi": {"present": True, "cf": 0.9}}}
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
                "demam_tinggi": {"present": True, "cf": 0.9},
                "batuk_kering": {"present": True, "cf": 0.8},
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

        payload = {"symptoms": {"demam_tinggi": {"present": True, "cf": 0.9}}}

        def make_request(request_id):
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
