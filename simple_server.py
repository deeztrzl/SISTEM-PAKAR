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
        rules_path = os.path.join(current_dir, "rules.json")
        inference_engine = InferenceEngine(rules_path)
        print(f"✅ Engine initialized with {len(inference_engine.rules)} rules")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return False


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "healthy",
            "engine_loaded": inference_engine is not None,
            "rules_count": len(inference_engine.rules) if inference_engine else 0,
        }
    )


@app.route("/api/status", methods=["GET"])
def status():
    """Alias untuk /api/health - digunakan oleh Jenkins"""
    return jsonify(
        {
            "status": "healthy",
            "engine_loaded": inference_engine is not None,
            "rules_count": len(inference_engine.rules) if inference_engine else 0,
        }
    )


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    try:
        print("📨 Received diagnosis request")

        if not inference_engine:
            return (
                jsonify(
                    {"success": False, "error": "Inference engine not initialized"}
                ),
                500,
            )

        # Get request data with error handling
        try:
            data = request.get_json()
        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            return (
                jsonify({"success": False, "error": f"Invalid JSON: {str(e)}"}),
                400,
            )

        print(f"📝 Request data: {data}")

        if not data or "symptoms" not in data:
            return (
                jsonify({"success": False, "error": "Missing symptoms in request"}),
                400,
            )

        symptoms = data["symptoms"]
        print(f"🔬 Symptoms to diagnose: {symptoms}")

        # Validate symptoms - handle both flat and nested formats
        validated_symptoms = {}
        for symptom, value in symptoms.items():
            try:
                # Handle nested format: {symptom: {present: bool, cf: value}}
                if isinstance(value, dict) and "cf" in value:
                    cf_float = float(value["cf"])
                # Handle flat format: {symptom: cf_value}
                else:
                    cf_float = float(value)

                if not (0.1 <= cf_float <= 1.0):
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"CF untuk {symptom} harus antara 0.1 dan 1.0",
                            }
                        ),
                        400,
                    )
                validated_symptoms[symptom] = cf_float
            except (ValueError, TypeError, AttributeError):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"CF untuk {symptom} harus berupa angka",
                        }
                    ),
                    400,
                )

        print(f"✅ Validated symptoms: {validated_symptoms}")

        # Run inference
        print("🔄 Running inference...")
        results = inference_engine.infer(validated_symptoms)
        print(f"✅ Inference completed: {len(results)} results")

        # Log hasil
        if results:
            print(
                f"🎯 Most likely: {results[0]['display_name']} (CF: {results[0]['cf']:.3f})"
            )

        # Wrap results dalam format yang sesuai untuk API
        response_data = {
            "success": True,
            "results": results,
            "most_likely_conclusion": results[0] if results else None,
            "total_results": len(results),
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"❌ Error in diagnosis: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


@app.route("/api/rules", methods=["GET"])
def get_rules():
    """Get all diagnostic rules"""
    try:
        if not inference_engine or not inference_engine.rules:
            return (
                jsonify({"success": False, "error": "No rules loaded"}),
                500,
            )

        return jsonify(
            {
                "success": True,
                "rules": inference_engine.rules,
                "total_rules": len(inference_engine.rules),
            }
        )
    except Exception as e:
        print(f"❌ Error retrieving rules: {e}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    print("🚀 Starting simple Flask diagnosis server...")

    if init_engine():
        print("🌐 Server starting on http://localhost:5000")
        app.run(host="localhost", port=5000, debug=True, use_reloader=False)
    else:
        print("💥 Failed to start server - engine initialization failed")
