import json
import os
from typing import List, Dict, Tuple


class InferenceEngine:
    """
    Forward Chaining Inference Engine dengan Certainty Factor

    Mendukung:
    - Forward chaining untuk inferensi
    - Penggabungan CF untuk aturan paralel dan sekuensial
    - Tracking aturan yang digunakan
    """

    def __init__(self, rules_file: str):
        """
        Inisialisasi inference engine dengan memuat rules dari file JSON

        Args:
            rules_file (str): Path ke file rules.json
        """
        self.rules = self.load_rules(rules_file)
        self.facts = {}  # {fact: cf_value}
        self.fired_rules = []  # Rules yang sudah dieksekusi
        self.inference_trace = []  # Jejak inferensi untuk debugging

    def load_rules(self, rules_file: str) -> List[Dict]:
        """
        Memuat rules dari file JSON

        Args:
            rules_file (str): Path ke file rules.json

        Returns:
            List[Dict]: Daftar rules

        Raises:
            FileNotFoundError: Jika file rules tidak ditemukan
            json.JSONDecodeError: Jika format JSON tidak valid
        """
        if not os.path.exists(rules_file):
            raise FileNotFoundError(f"Rules file tidak ditemukan: {rules_file}")

        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                rules = json.load(f)
            print(f"Berhasil memuat {len(rules)} rules dari {rules_file}")
            return rules
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Format JSON tidak valid dalam file {rules_file}", e.doc, e.pos
            )

    def add_initial_facts(self, initial_facts: Dict):
        """
        Menambahkan fakta awal dengan certainty factor

        Args:
            initial_facts (Dict): Dapat berupa:
                - Dict[str, float]: {fact: cf_value}
                - Dict[str, Dict]: {fact: {"present": bool, "cf": float}}

        Raises:
            ValueError: Jika CF tidak numeric atau diluar range [0, 1]
            TypeError: Jika struktur data tidak valid
        """
        for fact, value in initial_facts.items():
            # Extract CF value dari struktur yang berbeda
            if isinstance(value, dict):
                # Format: {"present": bool, "cf": float}
                if "cf" not in value:
                    raise KeyError(f"CF untuk {fact} tidak ditemukan dalam dict")
                cf = value["cf"]
            else:
                # Format: float value langsung
                cf = value

            # Validasi tipe data
            if not isinstance(cf, (int, float)):
                raise TypeError(
                    f"CF untuk {fact} harus numeric, got {type(cf).__name__}"
                )

            # Validasi range
            if not (0 <= cf <= 1):
                raise ValueError(f"CF untuk {fact} harus antara 0-1, got {cf}")

            # Store validated fact
            self.facts[fact] = cf
            self.inference_trace.append(f"Fakta awal: {fact} (CF: {cf:.2f})")

    def combine_certainty_factors(self, cf1: float, cf2: float) -> float:
        """
        Menggabungkan dua certainty factor untuk aturan paralel
        Formula: CF_combined = CF1 + CF2 - (CF1 * CF2)

        Args:
            cf1 (float): Certainty factor pertama
            cf2 (float): Certainty factor kedua

        Returns:
            float: Certainty factor gabungan
        """
        if cf1 < 0 or cf2 < 0:
            # Untuk CF negatif, gunakan formula berbeda
            return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
        else:
            return cf1 + cf2 - (cf1 * cf2)

    def calculate_rule_cf(self, rule: Dict) -> float:
        """
        Menghitung certainty factor untuk sebuah rule berdasarkan premis
        CF_rule = min(CF_premise1, CF_premise2, ...) * CF_rule

        Args:
            rule (Dict): Rule yang akan dihitung CF-nya

        Returns:
            float: Certainty factor untuk rule ini, atau 0 jika premis tidak terpenuhi
        """
        premises = rule["if"]
        premise_cfs = []

        # Cek semua premis ada di facts
        for premise in premises:
            if premise not in self.facts:
                return 0.0  # Premis tidak terpenuhi
            premise_cfs.append(self.facts[premise])

        # CF rule = minimum CF dari semua premis * CF rule
        min_premise_cf = min(premise_cfs)
        rule_cf = min_premise_cf * rule["cf"]

        return rule_cf

    def can_fire_rule(self, rule: Dict) -> bool:
        """
        Mengecek apakah sebuah rule dapat dieksekusi

        Args:
            rule (Dict): Rule yang akan dicek

        Returns:
            bool: True jika rule dapat dieksekusi
        """
        # Rule sudah pernah dieksekusi
        if rule["id"] in self.fired_rules:
            return False

        # Cek semua premis ada di facts
        for premise in rule["if"]:
            if premise not in self.facts:
                return False

        return True

    def forward_chaining(self) -> Dict[str, float]:
        """
        Melakukan forward chaining inference

        Returns:
            Dict[str, float]: Fakta-fakta yang diturunkan dengan CF
        """
        print("\\nMemulai Forward Chaining...")
        self.inference_trace.append("=== Mulai Forward Chaining ===")

        changed = True
        iteration = 0

        while (
            changed and iteration < 100
        ):  # Limit iterasi untuk menghindari infinite loop
            changed = False
            iteration += 1

            print(f"\\nIterasi {iteration}:")
            self.inference_trace.append(f"--- Iterasi {iteration} ---")

            for rule in self.rules:
                if self.can_fire_rule(rule):
                    rule_cf = self.calculate_rule_cf(rule)

                    if rule_cf > 0:
                        conclusion = rule["then"]

                        # Jika kesimpulan sudah ada (aturan paralel)
                        if conclusion in self.facts:
                            old_cf = self.facts[conclusion]
                            new_cf = self.combine_certainty_factors(old_cf, rule_cf)
                            self.facts[conclusion] = min(new_cf, 1.0)  # Cap di 1.0

                            trace_msg = f"Rule {rule['id']}: {' + '.join(rule['if'])} "
                            trace_msg += f"→ {conclusion}"
                            trace_msg += (
                                f" (CF: {rule_cf:.3f}, gabungan: {old_cf:.3f} + "
                            )
                            trace_msg += (
                                f"{rule_cf:.3f} = {self.facts[conclusion]:.3f})"
                            )
                            print(
                                f"  Aturan paralel {rule['id']}: {conclusion} CF "
                                f"{old_cf:.3f} → {self.facts[conclusion]:.3f}"
                            )

                        else:
                            # Kesimpulan baru (aturan sekuensial)
                            self.facts[conclusion] = rule_cf
                            trace_msg = f"Rule {rule['id']}: {' + '.join(rule['if'])} "
                            trace_msg += f"→ {conclusion} (CF: {rule_cf:.3f})"
                            print(
                                f"  Rule {rule['id']}: {conclusion} (CF: {rule_cf:.3f})"
                            )

                        self.inference_trace.append(trace_msg)
                        self.fired_rules.append(rule["id"])
                        changed = True

        print(f"\\nForward chaining selesai setelah {iteration} iterasi")
        print(f"Total rules yang dieksekusi: {len(self.fired_rules)}")

        return self.facts

    def get_conclusions(self, threshold: float = 0.5) -> Dict[str, float]:
        """
        Mendapatkan kesimpulan dengan CF di atas threshold

        Args:
            threshold (float): Batas minimum CF untuk kesimpulan

        Returns:
            Dict[str, float]: Kesimpulan dengan CF di atas threshold
        """
        conclusions = {}
        for fact, cf in self.facts.items():
            if cf >= threshold:
                conclusions[fact] = cf

        return conclusions

    def get_most_likely_conclusion(self) -> Tuple[str, float]:
        """
        Mendapatkan kesimpulan dengan CF tertinggi

        Returns:
            Tuple[str, float]: (kesimpulan, cf) dengan CF tertinggi
        """
        if not self.facts:
            return None, 0.0

        return max(self.facts.items(), key=lambda x: x[1])

    def get_inference_trace(self) -> List[str]:
        """
        Mendapatkan jejak inferensi untuk debugging

        Returns:
            List[str]: Jejak langkah-langkah inferensi
        """
        return self.inference_trace

    def reset(self):
        """
        Reset state untuk inferensi baru
        """
        self.facts = {}
        self.fired_rules = []
        self.inference_trace = []

    def infer(self, initial_facts: Dict) -> list:
        """
        Metode utama untuk melakukan inferensi dengan input gejala

        Args:
            initial_facts: Dictionary gejala dengan CF
                Format: {symptom: {"present": bool, "cf": float}}
                atau {symptom: cf_value} (deprecated)

        Returns:
            List[Dict]: Daftar hasil diagnosa diurutkan berdasarkan CF descending
                Setiap dict berisi: {"conclusion", "cf", "percentage", "display_name"}
        """
        # Reset engine state
        self.reset()

        # Add initial facts
        self.add_initial_facts(initial_facts)

        # Run forward chaining
        self.forward_chaining()

        # Get conclusions
        conclusions = self.get_conclusions(threshold=0.1)  # Lower threshold for demo

        # Format results for API
        formatted_results = []
        for conclusion, cf in conclusions.items():
            if conclusion not in initial_facts:
                # Exclude input symptoms from results
                formatted_results.append(
                    {
                        "conclusion": conclusion,
                        "cf": cf,
                        "percentage": round(cf * 100, 1),
                        "display_name": self.format_display_name(conclusion),
                    }
                )

        # Sort by confidence (descending)
        formatted_results.sort(key=lambda x: x["cf"], reverse=True)
        return formatted_results

    def format_display_name(self, name: str) -> str:
        """
        Format nama untuk display yang lebih readable

        Args:
            name: Nama asli (snake_case)

        Returns:
            Nama yang diformat untuk display
        """
        return name.replace("_", " ").title()

    def print_results(self, threshold: float = 0.0):
        """
        Mencetak hasil inferensi secara terformat

        Args:
            threshold (float): Batas minimum CF untuk ditampilkan
        """
        print("\\n" + "=" * 60)
        print("HASIL INFERENSI")
        print("=" * 60)

        if not self.facts:
            print("Tidak ada kesimpulan yang dapat ditarik.")
            return

        # Urutkan berdasarkan CF tertinggi
        sorted_facts = sorted(self.facts.items(), key=lambda x: x[1], reverse=True)

        print(f"\\nFakta yang diturunkan (CF ≥ {threshold}):")
        print("-" * 40)

        displayed_count = 0
        for fact, cf in sorted_facts:
            if cf >= threshold:
                if cf >= 0.8:
                    confidence_level = "Sangat Tinggi"
                elif cf >= 0.6:
                    confidence_level = "Tinggi"
                elif cf >= 0.4:
                    confidence_level = "Sedang"
                else:
                    confidence_level = "Rendah"
                print(f"{fact:30} | CF: {cf:.3f} | {confidence_level}")
                displayed_count += 1

        if displayed_count == 0:
            print(f"Tidak ada fakta dengan CF ≥ {threshold}")

        # Kesimpulan paling mungkin
        most_likely, highest_cf = self.get_most_likely_conclusion()
        if most_likely:
            print(f"\\nKesimpulan paling mungkin: {most_likely} (CF: {highest_cf:.3f})")

        print(f"\\nRules yang digunakan: {', '.join(self.fired_rules)}")
        print(f"Total fakta diturunkan: {len(self.facts)}")
