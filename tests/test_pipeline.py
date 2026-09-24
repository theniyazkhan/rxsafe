"""Unit tests for RxSafe components."""

import unittest
import pandas as pd
from src.catalogue import CatalogueLoader
from src.normalize import DrugNormalizer
from src.ddi import DDIEngine
from src.screen import ExactBrandDetector, GenericIngredientDetector, ClassLevelDetector
from src.inject import ErrorInjector
from src.metrics import calculate_precision_recall_f1, severity_weighted_recall


class TestRxSafePipeline(unittest.TestCase):

    def setUp(self):
        self.sample_catalogue = pd.DataFrame([
            {
                "brand_name": "Tylenol",
                "generic_name": "Acetaminophen",
                "drug_class": "Analgesic",
                "clean_brand": "tylenol",
                "clean_generic": "acetaminophen",
            },
            {
                "brand_name": "Advil",
                "generic_name": "Ibuprofen",
                "drug_class": "NSAID",
                "clean_brand": "advil",
                "clean_generic": "ibuprofen",
            },
            {
                "brand_name": "Motrin",
                "generic_name": "Ibuprofen",
                "drug_class": "NSAID",
                "clean_brand": "motrin",
                "clean_generic": "ibuprofen",
            },
        ])
        self.sample_ddi_data = pd.DataFrame([
            {
                "drug_a": "ibuprofen",
                "drug_b": "aspirin",
                "severity": "Major",
                "mechanism": "Increased bleeding risk",
            }
        ])

    def test_catalogue_clean(self):
        loader = CatalogueLoader()
        cleaned = loader.clean(self.sample_catalogue)
        self.assertIn("clean_brand", cleaned.columns)
        self.assertEqual(len(loader.get_known_brands()), 3)

    def test_normalizer(self):
        normalizer = DrugNormalizer(self.sample_catalogue)
        res = normalizer.pipeline("Tylenol")
        self.assertEqual(res["matched_brand"], "tylenol")
        self.assertEqual(res["generic_name"], "acetaminophen")
        self.assertEqual(res["drug_class"], "analgesic")

    def test_error_injection(self):
        injector = ErrorInjector(seed=42)
        corrupted = injector.inject_noise("Tylenol", error_rate=0.2)
        self.assertIsInstance(corrupted, str)

    def test_ddi_engine(self):
        engine = DDIEngine(self.sample_ddi_data)
        hit = engine.check_pair("aspirin", "ibuprofen")
        self.assertIsNotNone(hit)
        self.assertEqual(hit["severity"], "Major")

    def test_metrics(self):
        detected = [{"drug_a": "aspirin", "drug_b": "ibuprofen"}]
        gt = [{"drug_a": "aspirin", "drug_b": "ibuprofen", "severity": "Major"}]
        swr = severity_weighted_recall(detected, gt)
        self.assertEqual(swr, 1.0)


if __name__ == "__main__":
    unittest.main()
