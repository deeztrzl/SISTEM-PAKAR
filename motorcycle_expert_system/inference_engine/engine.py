import json
import os


class InferenceEngine:
    def __init__(self):
        self.rules = []
        self.symptoms = {}
        self.damages = {}
        self.facts = []
        self.inference_path = []

    def load_knowledge_base(self):
        """Load knowledge base from JSON files"""
        try:
            # Get the directory where this engine.py file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the main project directory
            base_dir = os.path.dirname(current_dir)

            rules_path = os.path.join(base_dir, "rules.json")
            symptoms_path = os.path.join(base_dir, "symptoms.json")
            damages_path = os.path.join(base_dir, "damages.json")

            with open(rules_path, "r", encoding="utf-8") as f:
                self.rules = json.load(f)

            with open(symptoms_path, "r", encoding="utf-8") as f:
                self.symptoms = json.load(f)

            with open(damages_path, "r", encoding="utf-8") as f:
                self.damages = json.load(f)

            return True
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return False

    def set_initial_facts(self, symptom_list):
        """Set initial facts from user input symptoms"""
        self.facts = symptom_list.copy()
        self.inference_path = []

    def combine_cf(self, cf1, cf2):
        """Combine Certainty Factors using CF combination formula"""
        if cf1 > 0 and cf2 > 0:
            return cf1 + cf2 - (cf1 * cf2)
        elif cf1 < 0 and cf2 < 0:
            return cf1 + cf2 + (cf1 * cf2)
        else:
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))

    def evaluate_rule(self, rule, current_facts):
        """Evaluate if a rule can be fired based on current facts"""
        rule_conditions = rule["if"]

        # Check if all conditions are met
        conditions_met = []
        for condition in rule_conditions:
            if condition in current_facts:
                conditions_met.append(condition)

        # Rule can fire if all conditions are met
        if len(conditions_met) == len(rule_conditions):
            return True, conditions_met

        return False, conditions_met

    def forward_chaining(self):
        """Main forward chaining algorithm with CF calculation"""
        derived_facts = {}  # Store conclusions with their CF values
        iteration = 0
        max_iterations = 10

        while iteration < max_iterations:
            iteration += 1
            new_facts_derived = False

            for rule in self.rules:
                can_fire, conditions_met = self.evaluate_rule(rule, self.facts)

                if can_fire:
                    conclusion = rule["then"]
                    rule_cf = rule["cf"]

                    # Record inference path
                    self.inference_path.append(
                        {
                            "rule_id": rule["id"],
                            "conditions": conditions_met,
                            "conclusion": conclusion,
                            "cf": rule_cf,
                            "description": rule.get("description", ""),
                        }
                    )

                    # Handle different types of conclusions
                    if conclusion.startswith("A"):  # Damage conclusion
                        if conclusion in derived_facts:
                            # Combine CF for parallel rules
                            old_cf = derived_facts[conclusion]
                            new_cf = self.combine_cf(old_cf, rule_cf)
                            derived_facts[conclusion] = new_cf
                        else:
                            derived_facts[conclusion] = rule_cf

                    elif conclusion.startswith(
                        "K"
                    ):  # Sequential rule (symptom as conclusion)
                        if conclusion not in self.facts:
                            self.facts.append(conclusion)
                            new_facts_derived = True

            # Stop if no new facts are derived
            if not new_facts_derived:
                break

        return derived_facts

    def get_diagnosis(self, symptom_list):
        """Main method to get diagnosis from symptoms"""
        self.set_initial_facts(symptom_list)

        if not self.load_knowledge_base():
            return self.create_fallback_diagnosis(symptom_list)

        # Run forward chaining
        results = self.forward_chaining()

        # If no results from forward chaining, use fallback mechanism
        if not results:
            return self.create_fallback_diagnosis(symptom_list)

        # Sort results by CF (highest first)
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        # Format diagnosis results
        diagnosis = []
        for damage_code, cf in sorted_results:
            if damage_code in self.damages:
                damage_info = self.damages[damage_code]
                diagnosis.append(
                    {
                        "code": damage_code,
                        "name": damage_info["name"],
                        "description": damage_info["description"],
                        "solution": damage_info["solution"],
                        "certainty_factor": round(cf, 3),
                        "confidence_percentage": round(cf * 100, 1),
                    }
                )

        return {
            "diagnosis": diagnosis,
            "inference_path": self.inference_path,
            "input_symptoms": [self.symptoms.get(s, s) for s in symptom_list],
        }

    def create_fallback_diagnosis(self, symptom_list):
        """Create fallback diagnosis when no exact rules match"""
        # Load knowledge base jika belum
        try:
            if not self.rules:
                self.load_knowledge_base()
        except Exception:
            pass

        # Hitung similarity score untuk setiap rule berdasarkan partial matching
        rule_scores = []

        for rule in self.rules:
            if rule["then"].startswith("A"):  # Hanya untuk kerusakan
                # Hitung berapa banyak kondisi rule yang match dengan gejala input
                matching_conditions = len(set(rule["if"]) & set(symptom_list))
                total_conditions = len(rule["if"])

                if matching_conditions > 0:
                    # Similarity score berdasarkan Jaccard similarity
                    similarity = matching_conditions / (
                        total_conditions + len(symptom_list) - matching_conditions
                    )
                    # CF dikalikan dengan similarity untuk partial matching
                    adjusted_cf = (
                        rule["cf"] * similarity * 0.5
                    )  # Reduced confidence for partial match

                    rule_scores.append(
                        {
                            "damage_code": rule["then"],
                            "cf": adjusted_cf,
                            "matching_symptoms": matching_conditions,
                            "rule_id": rule["id"],
                            "description": f"Partial match: {matching_conditions}/{total_conditions} kondisi terpenuhi",
                        }
                    )

        # Jika masih tidak ada partial match, berikan diagnosis umum berdasarkan kategori gejala
        if not rule_scores:
            rule_scores = self.create_category_based_diagnosis(symptom_list)

        # Sort by CF score
        rule_scores.sort(key=lambda x: x["cf"], reverse=True)

        # Ambil top 3 diagnosis dengan CF terbaik
        diagnosis = []
        for i, score in enumerate(rule_scores[:3]):
            if score["damage_code"] in self.damages:
                damage_info = self.damages[score["damage_code"]]
                diagnosis.append(
                    {
                        "code": score["damage_code"],
                        "name": damage_info["name"],
                        "description": damage_info["description"],
                        "solution": damage_info["solution"],
                        "certainty_factor": round(score["cf"], 3),
                        "confidence_percentage": round(score["cf"] * 100, 1),
                        "reason": score["description"],
                    }
                )

        # Tambahkan inference path untuk fallback
        fallback_path = [
            {
                "rule_id": "FALLBACK",
                "conditions": symptom_list,
                "conclusion": "Multiple possibilities",
                "cf": "Variable",
                "description": "Diagnosis berdasarkan partial matching karena tidak ada rule yang exact match",
            }
        ]

        return {
            "diagnosis": diagnosis,
            "inference_path": fallback_path,
            "input_symptoms": [self.symptoms.get(s, s) for s in symptom_list],
            "fallback_used": True,
        }

    def create_category_based_diagnosis(self, symptom_list):
        """Create diagnosis based on symptom categories when no partial matches found"""
        # Diagnosis umum berdasarkan pola gejala
        category_diagnosis = []

        # Mapping gejala ke kategori kerusakan umum
        electrical_symptoms = ["K01", "K02", "K03", "K04", "K29", "K30", "K31", "K32"]
        engine_symptoms = [
            "K05",
            "K06",
            "K07",
            "K08",
            "K09",
            "K13",
            "K14",
            "K16",
            "K17",
            "K20",
            "K34",
        ]
        fuel_symptoms = ["K10", "K11", "K12"]
        cvt_symptoms = ["K18", "K19"]
        brake_symptoms = ["K21", "K22", "K23", "K24"]
        suspension_symptoms = ["K25", "K26", "K27", "K28", "K33"]

        # Hitung overlap dengan setiap kategori
        electrical_count = len(set(symptom_list) & set(electrical_symptoms))
        engine_count = len(set(symptom_list) & set(engine_symptoms))
        fuel_count = len(set(symptom_list) & set(fuel_symptoms))
        cvt_count = len(set(symptom_list) & set(cvt_symptoms))
        brake_count = len(set(symptom_list) & set(brake_symptoms))
        suspension_count = len(set(symptom_list) & set(suspension_symptoms))

        # Berikan diagnosis berdasarkan kategori dengan gejala terbanyak
        if electrical_count > 0:
            category_diagnosis.append(
                {
                    "damage_code": "A01",
                    "cf": 0.3 + (electrical_count * 0.1),
                    "matching_symptoms": electrical_count,
                    "rule_id": "CAT_ELECTRICAL",
                    "description": f"Diagnosis kategori: {electrical_count} gejala kelistrikan",
                }
            )

        if engine_count > 0:
            category_diagnosis.append(
                {
                    "damage_code": "A04",
                    "cf": 0.3 + (engine_count * 0.1),
                    "matching_symptoms": engine_count,
                    "rule_id": "CAT_ENGINE",
                    "description": f"Diagnosis kategori: {engine_count} gejala mesin",
                }
            )

        if fuel_count > 0:
            category_diagnosis.append(
                {
                    "damage_code": "A02",
                    "cf": 0.3 + (fuel_count * 0.1),
                    "matching_symptoms": fuel_count,
                    "rule_id": "CAT_FUEL",
                    "description": f"Diagnosis kategori: {fuel_count} gejala bahan bakar",
                }
            )

        if cvt_count > 0:
            category_diagnosis.append(
                {
                    "damage_code": "A06",
                    "cf": 0.3 + (cvt_count * 0.1),
                    "matching_symptoms": cvt_count,
                    "rule_id": "CAT_CVT",
                    "description": f"Diagnosis kategori: {cvt_count} gejala CVT",
                }
            )

        if brake_count > 0:
            category_diagnosis.append(
                {
                    "damage_code": "A07",
                    "cf": 0.3 + (brake_count * 0.1),
                    "matching_symptoms": brake_count,
                    "rule_id": "CAT_BRAKE",
                    "description": f"Diagnosis kategori: {brake_count} gejala rem",
                }
            )

        if suspension_count > 0:
            category_diagnosis.append(
                {
                    "damage_code": "A08",
                    "cf": 0.3 + (suspension_count * 0.1),
                    "matching_symptoms": suspension_count,
                    "rule_id": "CAT_SUSPENSION",
                    "description": f"Diagnosis kategori: {suspension_count} gejala suspensi",
                }
            )

        # Jika tidak ada yang match, berikan diagnosis paling umum
        if not category_diagnosis:
            category_diagnosis.append(
                {
                    "damage_code": "A01",  # Default ke kelistrikan sebagai paling umum
                    "cf": 0.2,
                    "matching_symptoms": 0,
                    "rule_id": "DEFAULT",
                    "description": "Diagnosis default: Kemungkinan masalah sistem kelistrikan",
                }
            )

        return category_diagnosis

    def explain_reasoning(self, diagnosis_result):
        """Generate explanation of the reasoning process"""
        explanation = []

        explanation.append("=== PROSES INFERENSI FORWARD CHAINING ===")
        explanation.append(
            f"Gejala input: {', '.join(diagnosis_result['input_symptoms'])}"
        )
        explanation.append("")

        explanation.append("=== LANGKAH-LANGKAH INFERENSI ===")
        for i, step in enumerate(diagnosis_result["inference_path"], 1):
            explanation.append(f"Langkah {i}: {step['rule_id']}")
            explanation.append(
                f"  Kondisi: {', '.join([self.symptoms.get(c, c) for c in step['conditions']])}"
            )
            explanation.append(f"  Kesimpulan: {step['conclusion']}")
            explanation.append(f"  CF: {step['cf']}")
            explanation.append(f"  Deskripsi: {step['description']}")
            explanation.append("")

        explanation.append("=== HASIL DIAGNOSIS ===")
        for i, diag in enumerate(diagnosis_result["diagnosis"], 1):
            explanation.append(f"{i}. {diag['name']} ({diag['code']})")
            explanation.append(
                f"   Tingkat Kepercayaan: {diag['confidence_percentage']}%"
            )
            explanation.append(f"   Solusi: {diag['solution']}")
            explanation.append("")

        return "\n".join(explanation)


# Example usage
if __name__ == "__main__":
    # Test the inference engine
    engine = InferenceEngine()

    # Test with sample symptoms
    test_symptoms = [
        "K01",
        "K02",
        "K03",
    ]  # Motor tidak hidup, starter tidak fungsi, lampu tidak menyala

    result = engine.get_diagnosis(test_symptoms)

    if result:
        print("=== HASIL DIAGNOSIS ===")
        for diag in result["diagnosis"]:
            print(f"Kerusakan: {diag['name']}")
            print(f"Tingkat Kepercayaan: {diag['confidence_percentage']}%")
            print(f"Solusi: {diag['solution']}")
            print("-" * 50)

        print("\n=== PENJELASAN PROSES ===")
        print(engine.explain_reasoning(result))
    else:
        print("Tidak dapat melakukan diagnosis. Periksa file knowledge base.")
