#!/usr/bin/env python3
"""
Test direct diagnosis tanpa web server
"""

import sys
import os

# Add path untuk import
sys.path.append('.')

from inference_engine import InferenceEngine

def test_direct_diagnosis():
    print("Testing direct diagnosis...")
    
    try:
        # Load engine
        print("Loading inference engine...")
        engine = InferenceEngine('rules.json')
        print(f"✅ Engine loaded with {len(engine.rules)} rules")
        
        # Test infer method
        print("\nTesting diagnosis with symptoms: demam_tinggi=0.8, sakit_kepala=0.7")
        result = engine.infer({
            'demam_tinggi': 0.8,
            'sakit_kepala': 0.7
        })
        
        print(f"✅ Inference completed successfully")
        print(f"Success: {result.get('success')}")
        print(f"Results count: {len(result.get('results', []))}")
        print(f"Most likely: {result.get('most_likely_conclusion')}")
        print(f"Fired rules: {result.get('fired_rules')}")
        
        # Print detailed results
        if result.get('results'):
            print("\n📋 Detailed Results:")
            for i, res in enumerate(result['results'], 1):
                print(f"  {i}. {res['display_name']} (CF: {res['cf']:.3f}, {res['percentage']}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_diagnosis()
    if success:
        print("\n🎉 Direct diagnosis test PASSED!")
    else:
        print("\n💥 Direct diagnosis test FAILED!")