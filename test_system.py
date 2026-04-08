#!/usr/bin/env python3
"""
Test Script untuk Sistem Pakar
==============================

Script untuk testing otomatis functionality sistem pakar
"""

import os
import sys
import json

# Menambahkan path untuk import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inference_engine import InferenceEngine

def test_load_rules():
    """Test loading rules dari JSON"""
    print("Testing rule loading...")
    
    rules_path = os.path.join(os.path.dirname(__file__), 'rules.json')
    engine = InferenceEngine(rules_path)
    
    assert len(engine.rules) > 0, "Rules tidak berhasil dimuat"
    assert all('id' in rule for rule in engine.rules), "Semua rules harus memiliki ID"
    assert all('if' in rule for rule in engine.rules), "Semua rules harus memiliki premis"
    assert all('then' in rule for rule in engine.rules), "Semua rules harus memiliki kesimpulan"
    assert all('cf' in rule for rule in engine.rules), "Semua rules harus memiliki CF"
    
    print(f"✓ Berhasil memuat {len(engine.rules)} rules")

def test_certainty_factor_combination():
    """Test penggabungan certainty factor"""
    print("\\nTesting CF combination...")
    
    engine = InferenceEngine('rules.json')
    
    # Test combine CF
    cf1 = 0.6
    cf2 = 0.7
    combined = engine.combine_certainty_factors(cf1, cf2)
    expected = cf1 + cf2 - (cf1 * cf2)  # 0.6 + 0.7 - 0.42 = 0.88
    
    assert abs(combined - expected) < 0.001, f"CF combination salah: {combined} != {expected}"
    print(f"✓ CF combination: {cf1} + {cf2} = {combined:.3f}")

def test_sequential_rules():
    """Test aturan sekuensial"""
    print("\\nTesting sequential rules...")
    
    engine = InferenceEngine('rules.json')
    
    # Test case: demam_tinggi + sakit_kepala -> suspek_infeksi -> (dengan leukositosis) -> infeksi_bakteri
    symptoms = {
        'demam_tinggi': 0.8,
        'sakit_kepala': 0.7,
        'leukositosis': 0.9
    }
    
    engine.add_initial_facts(symptoms)
    results = engine.forward_chaining()
    
    # Cek apakah aturan sekuensial bekerja
    assert 'suspek_infeksi' in results, "Rule R1 tidak menghasilkan suspek_infeksi"
    assert 'infeksi_bakteri' in results, "Rule R4 (sekuensial) tidak bekerja"
    
    print("✓ Sequential rules berfungsi dengan baik")
    print(f"  suspek_infeksi: CF = {results.get('suspek_infeksi', 0):.3f}")
    print(f"  infeksi_bakteri: CF = {results.get('infeksi_bakteri', 0):.3f}")

def test_parallel_rules():
    """Test aturan paralel"""
    print("\\nTesting parallel rules...")
    
    engine = InferenceEngine('rules.json')
    
    # Test case: Dua cara berbeda untuk mendapatkan pneumonia
    symptoms = {
        'demam_tinggi': 0.9,
        'batuk_produktif': 0.8,
        'nyeri_dada': 0.7,
        'batuk_kering': 0.6,
        'sesak_napas': 0.8,
        'infiltrat_paru': 0.9
    }
    
    engine.add_initial_facts(symptoms)
    results = engine.forward_chaining()
    
    # Cek apakah aturan paralel menghasilkan pneumonia dengan CF gabungan
    assert 'pneumonia' in results, "Parallel rules tidak menghasilkan pneumonia"
    
    pneumonia_cf = results['pneumonia']
    assert pneumonia_cf > 0.5, "CF pneumonia dari parallel rules terlalu rendah"
    
    print("✓ Parallel rules berfungsi dengan baik")
    print(f"  pneumonia: CF = {pneumonia_cf:.3f}")

def test_inference_trace():
    """Test jejak inferensi"""
    print("\\nTesting inference trace...")
    
    engine = InferenceEngine('rules.json')
    
    symptoms = {'demam_tinggi': 0.8, 'sakit_kepala': 0.7}
    engine.add_initial_facts(symptoms)
    engine.forward_chaining()
    
    trace = engine.get_inference_trace()
    assert len(trace) > 0, "Inference trace kosong"
    
    print(f"✓ Inference trace berhasil: {len(trace)} langkah")

def test_edge_cases():
    """Test edge cases"""
    print("\\nTesting edge cases...")
    
    engine = InferenceEngine('rules.json')
    
    # Test CF ekstrem
    symptoms_extreme = {'demam_tinggi': 1.0, 'sakit_kepala': 0.1}
    engine.add_initial_facts(symptoms_extreme)
    results = engine.forward_chaining()
    
    # Pastikan tidak ada CF > 1.0
    for fact, cf in results.items():
        assert cf <= 1.0, f"CF untuk {fact} melebihi 1.0: {cf}"
        assert cf >= 0.0, f"CF untuk {fact} negatif: {cf}"
    
    print("✓ Edge cases handled correctly")

def test_comprehensive_scenario():
    """Test skenario komprehensif"""
    print("\\nTesting comprehensive scenario...")
    
    engine = InferenceEngine('rules.json')
    
    # Skenario kompleks: Pneumonia -> Pneumonia Berat -> Komplikasi Serius
    symptoms = {
        'demam_tinggi': 0.9,
        'batuk_produktif': 0.8,
        'nyeri_dada': 0.8,
        'gagal_napas': 0.9,
        'sepsis': 0.8
    }
    
    engine.add_initial_facts(symptoms)
    results = engine.forward_chaining()
    
    # Trace expected path
    expected_conclusions = ['pneumonia', 'pneumonia_berat', 'komplikasi_serius']
    
    for conclusion in expected_conclusions:
        if conclusion in results:
            print(f"  ✓ {conclusion}: CF = {results[conclusion]:.3f}")
        else:
            print(f"  ✗ {conclusion}: Not derived")
    
    print("✓ Comprehensive scenario completed")

def run_all_tests():
    """Menjalankan semua test"""
    print("="*60)
    print("TESTING SISTEM PAKAR DIAGNOSA MEDIS")
    print("="*60)
    
    tests = [
        test_load_rules,
        test_certainty_factor_combination,
        test_sequential_rules,
        test_parallel_rules,
        test_inference_trace,
        test_edge_cases,
        test_comprehensive_scenario
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
    
    print("\\n" + "="*60)
    print("HASIL TESTING")
    print("="*60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\\n🎉 Semua test BERHASIL! Sistem pakar berfungsi dengan baik.")
    else:
        print(f"\\n⚠️  {failed} test GAGAL. Perlu perbaikan.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)