"""Drug name normalization pipeline.

Maps raw brand strings (e.g. from OCR or human input) to standardized
generic active ingredients and pharmacological classes.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd

try:
    from rapidfuzz import process, fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    HAS_RAPIDFUZZ = False


class DrugNormalizer:
    """Normalizes raw medication names to canonical generic ingredients and classes."""

    def __init__(self, catalogue_df: Optional[pd.DataFrame] = None):
        self.brand_to_generic: Dict[str, str] = {}
        self.generic_to_class: Dict[str, str] = {}
        self.known_brands: List[str] = []

        if catalogue_df is not None and not catalogue_df.empty:
            self.build_index(catalogue_df)

    def build_index(self, catalogue_df: pd.DataFrame) -> None:
        """Build mapping lookup tables from cleaned catalogue DataFrame."""
        for _, row in catalogue_df.iterrows():
            brand = str(row.get("clean_brand", "")).lower().strip()
            generic = str(row.get("clean_generic", "")).lower().strip()
            dclass = str(row.get("drug_class", "")).lower().strip()

            if brand:
                self.brand_to_generic[brand] = generic
            if generic and dclass:
                self.generic_to_class[generic] = dclass

        self.known_brands = list(self.brand_to_generic.keys())

    def normalize_brand(self, raw_str: str, fuzzy_threshold: float = 80.0) -> Tuple[Optional[str], float]:
        """Map raw brand string to closest matching canonical brand name."""
        if not raw_str:
            return None, 0.0

        clean_str = raw_str.lower().strip()
        if clean_str in self.brand_to_generic:
            return clean_str, 100.0

        if not self.known_brands:
            return clean_str, 0.0

        if HAS_RAPIDFUZZ:
            match, score, _ = process.extractOne(
                clean_str, self.known_brands, scorer=fuzz.WRatio
            )
            if score >= fuzzy_threshold:
                return match, score
            return None, score
        else:
            matches = difflib.get_close_matches(
                clean_str, self.known_brands, n=1, cutoff=fuzzy_threshold / 100.0
            )
            if matches:
                ratio = difflib.SequenceMatcher(None, clean_str, matches[0]).ratio() * 100.0
                return matches[0], ratio
            return None, 0.0

    def to_generic(self, brand_name: str) -> Optional[str]:
        """Map brand name to generic drug ingredient."""
        if not brand_name:
            return None
        return self.brand_to_generic.get(brand_name.lower().strip())

    def to_class(self, generic_name: str) -> Optional[str]:
        """Map generic drug name to pharmacological class."""
        if not generic_name:
            return None
        return self.generic_to_class.get(generic_name.lower().strip())

    def pipeline(self, raw_str: str) -> Dict[str, Optional[str]]:
        """Full normalization pipeline: raw string -> brand -> generic -> class."""
        matched_brand, score = self.normalize_brand(raw_str)
        generic = self.to_generic(matched_brand) if matched_brand else None
        dclass = self.to_class(generic) if generic else None

        return {
            "raw_input": raw_str,
            "matched_brand": matched_brand,
            "match_score": score,
            "generic_name": generic,
            "drug_class": dclass,
        }
