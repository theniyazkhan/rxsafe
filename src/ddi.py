import pandas as pd


def _make_pair(drug_a: str, drug_b: str) -> tuple[str, str]:
    """Normalizes and sorts drug names for bidirectional lookup."""
    a = str(drug_a).strip().lower()
    b = str(drug_b).strip().lower()
    return min(a, b), max(a, b)


def load_ddi(path: str) -> dict:
    """Loads concatenated DDInter CSV into an O(1) lookup dictionary."""
    df = pd.read_csv(path)

    lookup = {}
    for drug_a, drug_b, level in zip(df["Drug_A"], df["Drug_B"], df["Level"]):
        severity = str(level).strip().lower()
        pair = _make_pair(drug_a, drug_b)
        lookup[pair] = severity

    return lookup


def get_interaction(drug_a: str, drug_b: str, lookup: dict):
    """Returns severity rating or None if no interaction is recorded."""
    pair = _make_pair(drug_a, drug_b)
    return lookup.get(pair, None)


if __name__ == "__main__":
    dataset_path = "data/external/ddinter_2026-09-26/ddinter_combined.csv"
    print(f"Loading lookup dictionary from {dataset_path}...")
    ddi_lookup = load_ddi(dataset_path)
    print(f"Loaded {len(ddi_lookup):,} unique interaction pairs.")

    # Test example lookup
    test_a, test_b = "Naltrexone", "Abacavir"
    res = get_interaction(test_a, test_b, ddi_lookup)
    print(f"Test Interaction ({test_a} + {test_b}): {res}")
