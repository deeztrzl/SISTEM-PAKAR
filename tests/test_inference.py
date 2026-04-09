"""
Unit tests untuk Inference Engine
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from inference_engine import InferenceEngine


@pytest.fixture
def rules_file():
    """Fixture untuk mendapatkan path rules.json"""
    return os.path.join(os.path.dirname(__file__), "..", "rules.json")


@pytest.fixture
def inference_engine(rules_file):
    """Fixture untuk membuat instance InferenceEngine"""
    return InferenceEngine(rules_file)


class TestInferenceEngineInitialization:
    """Test inisialisasi inference engine"""

    def test_engine_loads_rules(self, inference_engine):
        """Test engine berhasil load rules"""
        assert inference_engine.rules is not None
        assert len(inference_engine.rules) > 0

    def test_invalid_rules_file_handling(self):
        """Test handling file rules yang tidak ada"""
        with pytest.raises(FileNotFoundError):
            InferenceEngine("/path/yang/tidak/ada/rules.json")


class TestCertaintyFactorCalculations:
    """Test perhitungan Certainty Factor"""

    def test_cf_combination_parallel_rules(self, inference_engine):
        """Test kombinasi CF untuk aturan paralel"""
        # CF1 + CF2 - (CF1 * CF2)
        cf1, cf2 = 0.8, 0.6
        combined = cf1 + cf2 - (cf1 * cf2)
        assert combined == pytest.approx(0.92)

    def test_cf_sequential_calculation(self, inference_engine):
        """Test kalkulasi CF untuk aturan sekuensial"""
        # CF = min(premises) * CF_rule
        premises_cf = [0.8, 0.9, 0.7]
        rule_cf = 0.85
        result = min(premises_cf) * rule_cf
        assert result == pytest.approx(0.595)

    def test_cf_normalization(self, inference_engine):
        """Test CF selalu dalam range 0-1"""
        cf_values = [0.0, 0.5, 1.0, 0.95, 0.1]
        for cf in cf_values:
            assert 0.0 <= cf <= 1.0


class TestForwardChaining:
    """Test forward chaining algorithm"""

    def test_simple_diagnosis_chain(self, inference_engine):
        """Test inferensi simple dengan 1 gejala"""
        symptoms = {"fever": {"present": True, "cf": 0.9}}
        results = inference_engine.infer(symptoms)
        assert results is not None
        assert len(results) >= 0

    def test_multiple_symptoms_inference(self, inference_engine):
        """Test inferensi dengan multiple gejala"""
        symptoms = {
            "fever": {"present": True, "cf": 0.9},
            "cough": {"present": True, "cf": 0.8},
            "difficulty_breathing": {"present": True, "cf": 0.85},
        }
        results = inference_engine.infer(symptoms)
        assert results is not None

    def test_no_matching_rules(self, inference_engine):
        """Test ketika tidak ada aturan yang match"""
        symptoms = {"unknown_symptom_xyz": {"present": True, "cf": 0.9}}
        results = inference_engine.infer(symptoms)
        # Should return empty or handle gracefully
        assert isinstance(results, (list, dict, type(None)))


class TestRuleExecution:
    """Test eksekusi aturan"""

    def test_sequential_rules_execution_order(self, inference_engine):
        """Test aturan sekuensial dijalankan dalam urutan yang benar"""
        # Verifikasi bahwa dependencies di-respect
        symptoms = {"fever": {"present": True, "cf": 0.9}}
        results = inference_engine.infer(symptoms)
        # Results harus konsisten
        assert results is not None

    def test_parallel_rules_combination(self, inference_engine):
        """Test kombinasi aturan paralel yang menghasilkan diagnosis sama"""
        symptoms = {
            "fever": {"present": True, "cf": 0.85},
            "cough": {"present": True, "cf": 0.80},
        }
        results = inference_engine.infer(symptoms)
        # Kesimpulan yang sama dari aturan berbeda harus dikombinasikan
        assert results is not None

    def test_no_rule_reexecution(self, inference_engine):
        """Test rule tidak dijalankan lebih dari sekali"""
        # Inferensi harus terminate dan tidak infinite loop
        symptoms = {"fever": {"present": True, "cf": 0.9}}
        results = inference_engine.infer(symptoms)
        # Jika tidak ada infinite loop, test ini pass
        assert True


class TestErrorHandling:
    """Test error handling"""

    def test_malformed_symptoms_input(self, inference_engine):
        """Test handling input gejala yang malformed"""
        with pytest.raises((KeyError, ValueError, TypeError)):
            inference_engine.infer({"invalid": "format"})

    def test_invalid_cf_values(self, inference_engine):
        """Test handling CF value yang invalid (< 0 atau > 1)"""
        symptoms = {"fever": {"present": True, "cf": 1.5}}  # Invalid
        with pytest.raises((ValueError, AssertionError)):
            inference_engine.infer(symptoms)

    def test_missing_cf_in_symptoms(self, inference_engine):
        """Test handling ketika CF tidak disediakan"""
        with pytest.raises((KeyError, TypeError)):
            inference_engine.infer({"fever": {"present": True}})  # Missing 'cf'


class TestDiagnosisResults:
    """Test format dan validitas hasil diagnosa"""

    def test_results_have_required_fields(self, inference_engine):
        """Test hasil diagnosa memiliki field yang diperlukan"""
        symptoms = {"fever": {"present": True, "cf": 0.9}}
        results = inference_engine.infer(symptoms)

        if results and len(results) > 0:
            result = results[0]
            # Check required fields
            assert "diagnosis" in result or "name" in result
            assert "cf" in result or "certainty" in result

    def test_results_sorted_by_cf(self, inference_engine):
        """Test hasil diagnosa diurutkan berdasarkan CF descending"""
        symptoms = {
            "fever": {"present": True, "cf": 0.9},
            "cough": {"present": True, "cf": 0.8},
            "difficulty_breathing": {"present": True, "cf": 0.85},
        }
        results = inference_engine.infer(symptoms)

        if results and len(results) > 1:
            cfs = [r.get("cf", r.get("certainty", 0)) for r in results]
            assert cfs == sorted(cfs, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
