#!/usr/bin/env python3
"""
Flask Web Application untuk Sistem Pakar Diagnosa Medis
========================================================

Web-based interface untuk sistem pakar menggunakan Flask framework.
Menyediakan antarmuka modern dan responsive untuk input gejala dan diagnosa.

Features:
- RESTful API endpoints
- Modern responsive web interface
- Real-time diagnosis results
- Interactive symptom selection
- Visual certainty factor display
- Inference trace visualization

Author: Tim SISPAK 2
Version: 2.0 (Web Edition)
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Menambahkan path untuk import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from inference_engine import InferenceEngine
except ImportError as e:
    print(f"Error importing inference engine: {e}")
    sys.exit(1)

# Inisialisasi Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS untuk AJAX requests

# Konfigurasi
app.config["SECRET_KEY"] = "sispak2_medical_expert_system_2025"
app.config["DEBUG"] = True

# Global inference engine instance
inference_engine = None
available_symptoms = []


def init_inference_engine():
    """Inisialisasi inference engine dengan rules.json"""
    global inference_engine, available_symptoms

    try:
        rules_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "rules.json"
        )
        inference_engine = InferenceEngine(rules_path)

        # Extract available symptoms dari rules
        symptoms_set = set()
        for rule in inference_engine.rules:
            for symptom in rule["if"]:
                symptoms_set.add(symptom)

        available_symptoms = sorted(list(symptoms_set))

        print(
            f"✓ Inference engine initialized with {len(inference_engine.rules)} rules"
        )
        print(f"✓ Available symptoms: {len(available_symptoms)}")

    except Exception as e:
        print(f"✗ Error initializing inference engine: {e}")
        sys.exit(1)


@app.route("/")
def index():
    """Homepage - landing page sistem pakar"""
    return render_template("index.html")


@app.route("/diagnosis")
def diagnosis_page():
    """Halaman utama untuk diagnosa"""
    return render_template("diagnosis.html", symptoms=available_symptoms)


@app.route("/api/symptoms")
def get_symptoms():
    """API endpoint untuk mendapatkan daftar gejala"""
    symptoms_data = []
    for symptom in available_symptoms:
        display_name = symptom.replace("_", " ").title()
        symptoms_data.append(
            {
                "id": symptom,
                "name": display_name,
                "description": f"Gejala {display_name.lower()}",
            }
        )

    return jsonify(
        {"success": True, "symptoms": symptoms_data, "total": len(symptoms_data)}
    )


@app.route("/api/rules")
def get_rules():
    """API endpoint untuk mendapatkan daftar rules"""
    rules_data = []
    for rule in inference_engine.rules:
        premises = [p.replace("_", " ").title() for p in rule["if"]]
        conclusion = rule["then"].replace("_", " ").title()

        rules_data.append(
            {
                "id": rule["id"],
                "premises": premises,
                "conclusion": conclusion,
                "cf": rule["cf"],
                "description": rule.get("description", "Tidak ada deskripsi"),
            }
        )

    return jsonify({"success": True, "rules": rules_data, "total": len(rules_data)})


@app.route("/api/diagnose", methods=["POST"])
def api_diagnose():  # noqa: C901
    """API endpoint untuk melakukan diagnosa"""
    try:
        # Parse input JSON
        data = request.get_json()

        if not data or "symptoms" not in data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": 'Invalid input data. Expected JSON with "symptoms" field.',
                    }
                ),
                400,
            )

        symptoms = data["symptoms"]

        # Validasi input symptoms
        if not isinstance(symptoms, dict) or not symptoms:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Symptoms must be a non-empty dictionary of {symptom: cf_value}",
                    }
                ),
                400,
            )

        # Validasi CF values - handle both flat and nested formats
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
                                "error": f"CF untuk {symptom} harus antara 0.1 dan 1.0, diberikan: {cf_float}",
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
                            "error": f"CF untuk {symptom} harus berupa angka, diberikan: {value}",
                        }
                    ),
                    400,
                )

        # Jalankan inferensi menggunakan method infer yang baru
        try:
            results = inference_engine.infer(validated_symptoms)

            # Wrap results dalam response format yang sesuai untuk web API
            most_likely = results[0] if results else None
            response_data = {
                "success": True,
                "results": results,
                "most_likely_conclusion": most_likely,
                "total_results": len(results),
            }

        except Exception as e:
            print(f"Error during inference: {e}")
            return (
                jsonify(
                    {"success": False, "error": f"Error during inference: {str(e)}"}
                ),
                500,
            )

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in diagnose endpoint: {e}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


@app.route("/api/inference-trace", methods=["POST"])
def get_inference_trace():
    """API endpoint untuk mendapatkan jejak inferensi terakhir"""
    try:
        trace = inference_engine.get_inference_trace() if inference_engine else []

        return jsonify({"success": True, "trace": trace, "total_steps": len(trace)})

    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Error getting inference trace: {str(e)}"}
            ),
            500,
        )


@app.route("/rules")
def rules_page():
    """Halaman untuk melihat daftar rules"""
    return render_template("rules.html")


@app.route("/about")
def about_page():
    """Halaman informasi tentang sistem"""
    return render_template("about.html")


@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "Medical Expert System API",
            "version": "2.0",
            "inference_engine_loaded": inference_engine is not None,
            "total_rules": len(inference_engine.rules) if inference_engine else 0,
            "available_symptoms": len(available_symptoms),
        }
    )


def get_confidence_level(cf: float) -> str:
    """Mendapatkan level keyakinan berdasarkan CF"""
    if cf >= 0.8:
        return "Sangat Tinggi"
    elif cf >= 0.6:
        return "Tinggi"
    elif cf >= 0.4:
        return "Sedang"
    else:
        return "Rendah"


@app.errorhandler(404)
def not_found_error(error):
    """Error handler untuk 404"""
    return (
        render_template(
            "error.html", error_code=404, error_message="Halaman tidak ditemukan"
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Error handler untuk 500"""
    return (
        render_template(
            "error.html", error_code=500, error_message="Internal server error"
        ),
        500,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("SISTEM PAKAR DIAGNOSA MEDIS - WEB VERSION")
    print("=" * 60)
    print("Initializing web application...")

    # Initialize inference engine
    init_inference_engine()

    print("\\nStarting Flask development server...")
    print("Access the application at: http://localhost:5000")
    print("API Documentation: http://localhost:5000/api/health")
    print("\\nPress Ctrl+C to stop the server")
    print("=" * 60)

    # Run Flask app
    app.run(
        host="0.0.0.0",  # Allow external connections
        port=5000,
        debug=True,
        use_reloader=False,  # Avoid double initialization
    )
