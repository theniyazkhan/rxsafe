"""Drug-Drug Interaction (DDI) lookup engine.

Interface for querying known interactions between generic drug pairs or classes,
including severity rating and description retrieval.
"""

from typing import Dict, List, Optional, Set, Tuple
import pandas as pd


class DDIEngine:
    """Interaction lookup engine based on DDInter or custom interaction databases."""

    def __init__(self, ddi_df: Optional[pd.DataFrame] = None):
        self.interactions: Dict[Tuple[str, str], Dict[str, str]] = {}
        if ddi_df is not None and not ddi_df.empty:
            self.load_interactions(ddi_df)

    def load_interactions(self, ddi_df: pd.DataFrame) -> None:
        """Populate interaction lookup index from DataFrame."""
        for _, row in ddi_df.iterrows():
            drug_a = str(row.get("drug_a", "")).lower().strip()
            drug_b = str(row.get("drug_b", "")).lower().strip()
            severity = str(row.get("severity", "Unknown")).strip()
            mechanism = str(row.get("mechanism", "")).strip()

            if drug_a and drug_b:
                pair = tuple(sorted([drug_a, drug_b]))
                self.interactions[pair] = {
                    "severity": severity,
                    "mechanism": mechanism,
                }

    def check_pair(self, drug_a: str, drug_b: str) -> Optional[Dict[str, str]]:
        """Check if interaction exists between two generic drug names."""
        pair = tuple(sorted([drug_a.lower().strip(), drug_b.lower().strip()]))
        return self.interactions.get(pair)

    def find_all_interactions(self, drug_list: List[str]) -> List[Dict[str, str]]:
        """Find all pairwise interactions within a list of generic drugs."""
        clean_list = list(set([d.lower().strip() for d in drug_list if d]))
        results = []

        for i in range(len(clean_list)):
            for j in range(i + 1, len(clean_list)):
                drug_a, drug_b = clean_list[i], clean_list[j]
                match = self.check_pair(drug_a, drug_b)
                if match:
                    results.append({
                        "drug_a": drug_a,
                        "drug_b": drug_b,
                        "severity": match["severity"],
                        "mechanism": match["mechanism"],
                    })

        return results
