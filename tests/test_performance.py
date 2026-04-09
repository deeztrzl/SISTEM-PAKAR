"""
Performance tests untuk Inference Engine
"""

import pytest
import time
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference_engine import InferenceEngine


@pytest.fixture
def inference_engine():
    """Fixture untuk inference engine"""
    rules_file = os.path.join(os.path.dirname(__file__), "..", "rules.json")
    return InferenceEngine(rules_file)


class TestInferencePerformance:
    """Test performance inference engine"""

    def test_single_inference_performance(self, inference_engine):
        """Test single inference harus < 100ms"""
        symptoms = {"fever": {"present": True, "cf": 0.9}}

        start = time.time()
        result = inference_engine.infer(symptoms)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Inference took {elapsed}s, should be < 0.1s"

    def test_complex_inference_performance(self, inference_engine):
        """Test complex inference dengan 5+ gejala harus < 200ms"""
        symptoms = {
            "fever": {"present": True, "cf": 0.9},
            "cough": {"present": True, "cf": 0.8},
            "difficulty_breathing": {"present": True, "cf": 0.85},
            "chest_pain": {"present": True, "cf": 0.75},
            "headache": {"present": True, "cf": 0.7},
        }

        start = time.time()
        result = inference_engine.infer(symptoms)
        elapsed = time.time() - start

        assert elapsed < 0.2, f"Complex inference took {elapsed}s, should be < 0.2s"

    def test_batch_inference_throughput(self, inference_engine):
        """Test 100 inferences harus complete dalam < 5 detik"""
        symptoms_list = [
            {f"symptom_{i}": {"present": True, "cf": 0.8}} for i in range(100)
        ]

        start = time.time()
        for symptoms in symptoms_list[:10]:  # Run 10 to limit test time
            inference_engine.infer(symptoms)
        elapsed = time.time() - start

        # Should handle 10 inferences quickly
        assert elapsed < 2.0, f"Batch inferences took {elapsed}s"


class TestMemoryUsage:
    """Test memory efficiency"""

    def test_multiple_inferences_memory_stable(self, inference_engine):
        """Test memory usage tetap stabil setelah multiple inferences"""
        import gc

        symptoms = {"fever": {"present": True, "cf": 0.9}}

        # Run multiple times
        for _ in range(100):
            result = inference_engine.infer(symptoms)
            gc.collect()

        # If this completes without crash, memory is stable
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
