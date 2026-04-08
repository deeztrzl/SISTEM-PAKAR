#!/usr/bin/env python3
"""
Simple Flask app untuk debug diagnosis API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add path untuk import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from inference_engine import InferenceEngine

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global inference engine
inference_engine = None

def init_engine():
    global inference_engine
    try:
        rules_path = os.path.join(parent_dir, 'rules.json')
        inference_engine = InferenceEngine(rules_path)
        print(f"✅ Engine initialized with {len(inference_engine.rules)} rules")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'engine_loaded': inference_engine is not None,
        'rules_count': len(inference_engine.rules) if inference_engine else 0
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Alias untuk /api/health - digunakan oleh Jenkins"""
    return jsonify({
        'status': 'healthy',
        'engine_loaded': inference_engine is not None,
        'rules_count': len(inference_engine.rules) if inference_engine else 0
    })

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    try:
        print("📨 Received diagnosis request")
        
        if not inference_engine:
            return jsonify({
                'success': False,
                'error': 'Inference engine not initialized'
            }), 500
        
        # Get request data
        data = request.get_json()
        print(f"📝 Request data: {data}")
        
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing symptoms in request'
            }), 400
        
        symptoms = data['symptoms']
        print(f"🔬 Symptoms to diagnose: {symptoms}")
        
        # Validate symptoms
        validated_symptoms = {}
        for symptom, cf in symptoms.items():
            try:
                cf_float = float(cf)
                if not (0.1 <= cf_float <= 1.0):
                    return jsonify({
                        'success': False,
                        'error': f'CF untuk {symptom} harus antara 0.1 dan 1.0'
                    }), 400
                validated_symptoms[symptom] = cf_float
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': f'CF untuk {symptom} harus berupa angka'
                }), 400
        
        print(f"✅ Validated symptoms: {validated_symptoms}")
        
        # Run inference
        print("🔄 Running inference...")
        result = inference_engine.infer(validated_symptoms)
        print(f"✅ Inference completed: {result.get('success')}")
        
        # Log hasil
        if result.get('most_likely_conclusion'):
            print(f"🎯 Most likely: {result['most_likely_conclusion']['display_name']} (CF: {result['most_likely_conclusion']['cf']:.3f})")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting simple Flask diagnosis server...")
    
    if init_engine():
        print("🌐 Server starting on http://localhost:5000")
        app.run(host='localhost', port=5000, debug=True, use_reloader=False)
    else:
        print("💥 Failed to start server - engine initialization failed")