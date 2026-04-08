#!/usr/bin/env python3
"""
Test script untuk API diagnosis
"""

import requests
import json

def test_diagnosis_api():
    url = "http://localhost:5000/api/diagnose"
    data = {
        "symptoms": {
            "demam_tinggi": 0.8,
            "sakit_kepala": 0.7
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing diagnosis API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nResponse Body:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                print(f"\n✅ SUCCESS!")
                print(f"Most likely conclusion: {result.get('most_likely_conclusion')}")
                print(f"Total results: {len(result.get('results', []))}")
                print(f"Fired rules: {result.get('fired_rules')}")
            else:
                print(f"\n❌ API returned error: {result.get('error')}")
        else:
            print(f"\n❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server tidak dapat dijangkau")
        print("Pastikan Flask server berjalan di http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_diagnosis_api()