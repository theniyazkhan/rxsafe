import itertools
import os
import sys

# Ensure root workspace is in sys.path when script is run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.ddi import get_interaction, load_ddi
except ModuleNotFoundError:
    from ddi import get_interaction, load_ddi


def check_interactions(rx_id: str, generics: list[str], lookup: dict) -> list[dict]:
    """
    Evaluates all pairwise combinations of generics against the DDI lookup table.
    Outputs alerts following the agreed thesis schema.
    """
    alerts = []
    # Clean and deduplicate generic names
    cleaned_generics = list({g.strip().lower() for g in generics if g and isinstance(g, str)})

    # Evaluate every unique pairwise combination (n choose 2)
    for drug_a, drug_b in itertools.combinations(cleaned_generics, 2):
        severity = get_interaction(drug_a, drug_b, lookup)
        if severity:
            alerts.append({
                "rx_id": rx_id,
                "alert_type": "ddi",
                "drug_a": drug_a,
                "drug_b": drug_b,
                "severity": severity
            })

    return alerts


def check_polypharmacy(rx_id: str, generics: list[str], threshold: int = 5) -> list[dict]:
    """Flag prescriptions with active generic count exceeding threshold."""
    unique_generics = {g.strip().lower() for g in generics if g}
    if len(unique_generics) >= threshold:
        return [{
            "rx_id": rx_id,
            "alert_type": "polypharmacy",
            "drug_a": f"count_{len(unique_generics)}",
            "drug_b": "N/A",
            "severity": "Warning"
        }]
    return []


def check_antimicrobial(rx_id: str, generics: list[str]) -> list[dict]:
    """Stub for co-prescribed or redundant antimicrobial screening (Week 3)."""
    return []


if __name__ == "__main__":
    # Smoke test
    print("Testing screen.py...")
    ddi_path = "data/external/ddinter_2026-09-26/ddinter_combined.csv"
    lookup = load_ddi(ddi_path)

    # Simulated prescription with a known interacting pair and an inert drug
    sample_rx = ["naltrexone", "abacavir", "paracetamol"]
    results = check_interactions("RX_TEST_001", sample_rx, lookup)

    print(f"Generated {len(results)} alert(s):")
    for alert in results:
        print(f"  [{alert['alert_type'].upper()}] {alert['drug_a']} <-> {alert['drug_b']} | Severity: {alert['severity']}")