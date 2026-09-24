"""Product catalogue loader and cleaning utility.

Handles ingestion, normalization of schema, handling missing attributes,
and indexing of pharmaceutical product catalogues.
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


class CatalogueLoader:
    """Loader and indexer for medication product catalogues."""

    def __init__(self, catalogue_path: Optional[Path] = None):
        self.catalogue_path = catalogue_path
        self.df: Optional[pd.DataFrame] = None

    def load_raw_catalogue(self, path: Optional[Path] = None) -> pd.DataFrame:
        """Load raw catalogue dataset from CSV/Parquet file."""
        target_path = path or self.catalogue_path
        if not target_path or not Path(target_path).exists():
            # Return empty skeleton if file not yet present
            return pd.DataFrame(columns=[
                "brand_name", "generic_name", "drug_class", "strength", "dosage_form"
            ])
        
        if str(target_path).endswith(".csv"):
            self.df = pd.read_csv(target_path)
        elif str(target_path).endswith(".parquet"):
            self.df = pd.read_parquet(target_path)
        else:
            raise ValueError(f"Unsupported file format for {target_path}")

        return self.df

    def clean(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Clean and normalize catalogue entries."""
        data = df if df is not None else self.df
        if data is None or data.empty:
            return pd.DataFrame(columns=[
                "brand_name", "generic_name", "drug_class", "strength", "dosage_form",
                "clean_brand", "clean_generic"
            ])

        cleaned = data.copy()
        for col in ["brand_name", "generic_name", "drug_class"]:
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].astype(str).str.strip()

        cleaned["clean_brand"] = cleaned["brand_name"].str.lower()
        cleaned["clean_generic"] = cleaned["generic_name"].str.lower()
        
        self.df = cleaned
        return cleaned

    def get_known_brands(self) -> List[str]:
        """Return list of distinct clean brand names in catalogue."""
        if self.df is None or "clean_brand" not in self.df.columns:
            return []
        return list(self.df["clean_brand"].dropna().unique())
