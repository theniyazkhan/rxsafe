SEVERITY_WEIGHTS = {
    "major": 3.0,
    "moderate": 2.0,
    "minor": 1.0
}

def _canonical_pair(drug_a: str, drug_b: str) -> tuple[str, str]:
    a, b = drug_a.strip().lower(), drug_b.strip().lower()
    return (min(a, b), max(a, b))

def calculate_metrics(
    ground_truth_alerts: list[dict],
    predicted_alerts: list[dict],
    total_prescriptions: int = 1,
    abstained_prescriptions: int = 0
) -> dict:
    gt_map = {}
    for alert in ground_truth_alerts:
        if alert.get("alert_type") == "ddi":
            pair = _canonical_pair(alert["drug_a"], alert["drug_b"])
            sev = str(alert.get("severity", "minor")).strip().lower()
            gt_map[pair] = SEVERITY_WEIGHTS.get(sev, 1.0)

    pred_pairs = set()
    for alert in predicted_alerts:
        if alert.get("alert_type") == "ddi":
            pair = _canonical_pair(alert["drug_a"], alert["drug_b"])
            pred_pairs.add(pair)

    true_positive_pairs = set(gt_map.keys()) & pred_pairs

    precision = len(true_positive_pairs) / len(pred_pairs) if pred_pairs else 0.0
    recall = len(true_positive_pairs) / len(gt_map) if gt_map else 0.0

    total_gt_weight = sum(gt_map.values())
    detected_weight = sum(gt_map[pair] for pair in true_positive_pairs)
    severity_weighted_recall = (
        detected_weight / total_gt_weight if total_gt_weight > 0 else 0.0
    )

    abstention_rate = (
        abstained_prescriptions / total_prescriptions if total_prescriptions > 0 else 0.0
    )

    return {
        "ground_truth_count": len(gt_map),
        "predicted_count": len(pred_pairs),
        "true_positives": len(true_positive_pairs),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "severity_weighted_recall": round(severity_weighted_recall, 4),
        "abstention_rate": round(abstention_rate, 4),
    }

if __name__ == "__main__":
    print("Running metrics smoke test...")
    gt = [
        {"alert_type": "ddi", "drug_a": "ciprofloxacin", "drug_b": "theophylline", "severity": "Major"},
        {"alert_type": "ddi", "drug_a": "aspirin", "drug_b": "paracetamol", "severity": "Minor"}
    ]
    preds = [
        {"alert_type": "ddi", "drug_a": "paracetamol", "drug_b": "aspirin", "severity": "Minor"}
    ]
    res = calculate_metrics(gt, preds)
    print(f"Standard Recall:          {res['recall'] * 100:.1f}%")
    print(f"Severity-Weighted Recall: {res['severity_weighted_recall'] * 100:.1f}%")
