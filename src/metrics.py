"""Evaluation metrics for medication safety screening.

Includes standard metrics (Precision, Recall, F1) as well as domain-specific
metrics such as Severity-Weighted Recall for Drug-Drug Interactions.
"""

from typing import Dict, List, Set, Tuple, Union

SEVERITY_WEIGHTS = {
    "contraindicated": 1.0,
    "major": 0.8,
    "severe": 0.8,
    "moderate": 0.5,
    "minor": 0.2,
    "unknown": 0.1,
}


def calculate_precision_recall_f1(
    predictions: Set[Tuple[str, str]], ground_truth: Set[Tuple[str, str]]
) -> Dict[str, float]:
    """Calculate standard precision, recall, and F1 score for detected DDI pairs."""
    if not predictions:
        return {
            "precision": 1.0 if not ground_truth else 0.0,
            "recall": 1.0 if not ground_truth else 0.0,
            "f1": 1.0 if not ground_truth else 0.0,
        }

    tp = len(predictions.intersection(ground_truth))
    fp = len(predictions - ground_truth)
    fn = len(ground_truth - predictions)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def severity_weighted_recall(
    detected_ddis: List[Dict[str, str]],
    ground_truth_ddis: List[Dict[str, str]],
) -> float:
    """Calculate severity-weighted recall for DDI detection.

    Gives higher penalty for missing high-severity (e.g. Contraindicated/Major) DDIs.
    """
    if not ground_truth_ddis:
        return 1.0

    total_weight = 0.0
    detected_weight = 0.0

    # Index detected pairs
    detected_pairs = {
        tuple(sorted([d["drug_a"].lower(), d["drug_b"].lower()]))
        for d in detected_ddis
    }

    for gt in ground_truth_ddis:
        pair = tuple(sorted([gt["drug_a"].lower(), gt["drug_b"].lower()]))
        severity = str(gt.get("severity", "unknown")).lower()
        weight = SEVERITY_WEIGHTS.get(severity, 0.1)

        total_weight += weight
        if pair in detected_pairs:
            detected_weight += weight

    return detected_weight / total_weight if total_weight > 0 else 0.0
