from flask import Flask, render_template, request, jsonify
import json
import sys
import os

# Get the absolute path of the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to the path so we can import the inference engine
sys.path.append(BASE_DIR)
from inference_engine.engine import InferenceEngine

app = Flask(__name__)

# Initialize inference engine
engine = InferenceEngine()

@app.route('/')
def index():
    """Main page with symptom checklist"""
    try:
        symptoms_path = os.path.join(BASE_DIR, 'symptoms.json')
        symptoms_categorized_path = os.path.join(BASE_DIR, 'symptoms_categorized.json')
        
        with open(symptoms_path, 'r', encoding='utf-8') as f:
            symptoms = json.load(f)
        
        with open(symptoms_categorized_path, 'r', encoding='utf-8') as f:
            symptoms_categorized = json.load(f)
            
        return render_template('index.html', 
                             symptoms=symptoms, 
                             symptoms_categorized=symptoms_categorized)
    except Exception as e:
        return f"Error loading symptoms: {e}"

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """Process diagnosis request"""
    try:
        data = request.get_json()
        selected_symptoms = data.get('symptoms', [])
        
        if not selected_symptoms:
            return jsonify({'error': 'Tidak ada gejala yang dipilih'})
        
        # Get diagnosis from inference engine
        result = engine.get_diagnosis(selected_symptoms)
        
        # Sistem selalu memberikan diagnosis, tidak pernah None
        return jsonify({
            'success': True,
            'diagnosis': result['diagnosis'],
            'inference_path': result['inference_path'],
            'input_symptoms': result['input_symptoms'],
            'fallback_used': result.get('fallback_used', False)
        })
            
    except Exception as e:
        return jsonify({'error': f'Error dalam proses diagnosis: {str(e)}'})

@app.route('/api/symptoms')
def get_symptoms():
    """API endpoint to get all symptoms"""
    try:
        symptoms_path = os.path.join(BASE_DIR, 'symptoms.json')
        with open(symptoms_path, 'r', encoding='utf-8') as f:
            symptoms = json.load(f)
        return jsonify(symptoms)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/damages')
def get_damages():
    """API endpoint to get all damages"""
    try:
        damages_path = os.path.join(BASE_DIR, 'damages.json')
        with open(damages_path, 'r', encoding='utf-8') as f:
            damages = json.load(f)
        return jsonify(damages)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/rules')
def get_rules():
    """API endpoint to get all rules"""
    try:
        rules_path = os.path.join(BASE_DIR, 'rules.json')
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        return jsonify(rules)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)