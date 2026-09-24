"""Experiment runner for error propagation and decomposition analysis.

Orchestrates full experimental sweeps across error injection rates, optical recognition backends,
normalization methods, and safety detectors.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.catalogue import CatalogueLoader
from src.normalize import DrugNormalizer
from src.ddi import DDIEngine
from src.screen import ExactBrandDetector, GenericIngredientDetector, ClassLevelDetector
from src.inject import ErrorInjector
from src.metrics import calculate_precision_recall_f1, severity_weighted_recall


class ExperimentRunner:
    """Executes propagation and decomposition experiments."""

    def __init__(
        self,
        catalogue_path: Optional[Path] = None,
        ddi_path: Optional[Path] = None,
        output_dir: Path = Path("results/runs"),
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.catalogue_loader = CatalogueLoader(catalogue_path)
        self.ddi_engine = DDIEngine()
        self.normalizer = DrugNormalizer()

    def run_propagation_experiment(
        self,
        prescriptions: List[List[str]],
        ground_truth_ddis: List[List[Dict[str, str]]],
        error_rates: List[float] = [0.0, 0.05, 0.1, 0.2, 0.3],
        seed: int = 42,
    ) -> Path:
        """Run error propagation sweep across noise levels."""
        injector = ErrorInjector(seed=seed)
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"run_{date_str}_seed{seed}"
        run_folder = self.output_dir / run_name
        run_folder.mkdir(parents=True, exist_ok=True)

        results = []

        for rate in error_rates:
            rate_results = {
                "error_rate": rate,
                "exact_detector": [],
                "generic_detector": [],
            }

            detector_exact = ExactBrandDetector(self.ddi_engine)
            detector_generic = GenericIngredientDetector(self.normalizer, self.ddi_engine)

            for rx, gt in zip(prescriptions, ground_truth_ddis):
                # Corrupt brands
                corrupted_rx = injector.corrupt_prescription(rx, error_rate=rate)

                # Screen
                exact_hits = detector_exact.screen(corrupted_rx)
                generic_hits = detector_generic.screen(corrupted_rx)

                # Evaluate
                sw_recall_exact = severity_weighted_recall(exact_hits, gt)
                sw_recall_generic = severity_weighted_recall(generic_hits, gt)

                rate_results["exact_detector"].append({"sw_recall": sw_recall_exact})
                rate_results["generic_detector"].append({"sw_recall": sw_recall_generic})

            results.append(rate_results)

        # Save run summary
        summary_path = run_folder / "experiment_results.json"
        with open(summary_path, "w") as f:
            json.dump({"seed": seed, "run_name": run_name, "results": results}, f, indent=2)

        return summary_path
