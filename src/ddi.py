import pandas as pd


def load_ddi(path: str) -> dict:
    """Loads concatenated DDInter CSV into an O(1) lookup dictionary."""
    df = pd.read_csv(path)

    lookup = {}
    for drug_a, drug_b, level in zip(df["Drug_A"], df["Drug_B"], df["Level"]):
        a = str(drug_a).strip().lower()
        b = str(drug_b).strip().lower()
        severity = str(level).strip()

        # Store normalized, sorted pair to allow bidirectional lookup
        pair = (min(a, b), max(a, b))
        lookup[pair] = severity

    return lookup


def get_interaction(drug_a: str, drug_b: str, lookup: dict):
    """Returns severity rating or None if no interaction is recorded."""
    a = drug_a.strip().lower()
    b = drug_b.strip().lower()
    pair = (min(a, b), max(a, b))
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
