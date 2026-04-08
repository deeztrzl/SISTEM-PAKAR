"""
Inference Engine Package
========================

Paket ini berisi implementasi inference engine untuk sistem pakar
dengan forward chaining dan certainty factor.

Modules:
- forward_chaining: Implementasi algoritma forward chaining
"""

from .forward_chaining import InferenceEngine

__all__ = ['InferenceEngine']