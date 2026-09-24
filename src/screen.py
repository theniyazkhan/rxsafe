"""Safety screening detectors.

Implements the three detector paradigms for evaluating medication safety:
1. Exact Brand/String Level Detector
2. Generic/Ingredient Level Detector
3. Class-Level / Mechanistic Safety Detector
"""

from typing import Dict, List, Any
from src.normalize import DrugNormalizer
from src.ddi import DDIEngine


class ExactBrandDetector:
    """Detector 1: Direct brand-name matching without normalization."""

    def __init__(self, ddi_engine: DDIEngine):
        self.ddi_engine = ddi_engine

    def screen(self, raw_brands: List[str]) -> List[Dict[str, Any]]:
        """Screen raw brand names directly against DDI database."""
        return self.ddi_engine.find_all_interactions(raw_brands)


class GenericIngredientDetector:
    """Detector 2: Brand -> Generic normalized interaction screening."""

    def __init__(self, normalizer: DrugNormalizer, ddi_engine: DDIEngine):
        self.normalizer = normalizer
        self.ddi_engine = ddi_engine

    def screen(self, raw_brands: List[str]) -> List[Dict[str, Any]]:
        """Map raw brand strings to generic drugs and screen for DDIs."""
        generics = []
        for brand in raw_brands:
            norm = self.normalizer.pipeline(brand)
            if norm["generic_name"]:
                generics.append(norm["generic_name"])

        return self.ddi_engine.find_all_interactions(generics)


class ClassLevelDetector:
    """Detector 3: Pharmacological class level safety & duplicate therapy detector."""

    def __init__(self, normalizer: DrugNormalizer, ddi_engine: DDIEngine):
        self.normalizer = normalizer
        self.ddi_engine = ddi_engine

    def screen(self, raw_brands: List[str]) -> Dict[str, Any]:
        """Screen for DDIs and therapeutic duplications at the class level."""
        generic_ddis = GenericIngredientDetector(self.normalizer, self.ddi_engine).screen(raw_brands)
        
        class_counts: Dict[str, List[str]] = {}
        for brand in raw_brands:
            norm = self.normalizer.pipeline(brand)
            dclass = norm.get("drug_class")
            generic = norm.get("generic_name") or brand
            if dclass:
                class_counts.setdefault(dclass, []).append(generic)

        duplicate_therapies = {
            dclass: drugs for dclass, drugs in class_counts.items() if len(drugs) > 1
        }

        return {
            "pairwise_ddis": generic_ddis,
            "duplicate_therapies": duplicate_therapies,
        }
