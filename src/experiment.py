import os
import argparse
import pandas as pd
from datetime import datetime
from src.catalogue import load_catalogue, expand_catalogue
from src.normalize import build_index, normalize_one
from src.ddi import load_ddi
from src.screen import check_interactions


def run_pipeline(input_path: str, threshold: float = 0.80):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("results", "runs", run_id)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load Knowledge Layer (Sections 5.1, 5.2, 5.4)
    cat_raw = load_catalogue("data/external/catalogue_2026-09-26/medicine.csv")
    cat = expand_catalogue(cat_raw)
    brand_list = build_index(cat)
    ddi_table = load_ddi("data/external/ddinter_2026-09-26/ddinter_combined.csv")

    # 2. Read prescription input strings
    rx_df = pd.read_csv(input_path)  # Expects columns: rx_id, brand_string
    
    all_alerts = []
    for rx_id, group in rx_df.groupby("rx_id"):
        generics = []
        for raw_brand in group["brand_string"]:
            norm = normalize_one(raw_brand, brand_list, cat, threshold)
            if not norm["abstained"] and norm["matched_generic"]:
                generics.extend(norm["matched_generic"])
        
        rx_alerts = check_interactions(generics, ddi_table)
        for a in rx_alerts:
            a["rx_id"] = rx_id
            all_alerts.append(a)

    # 3. Save Output
    out_file = os.path.join(out_dir, "alerts.csv")
    pd.DataFrame(all_alerts).to_csv(out_file, index=False)
    print(f"Run completed successfully. Alerts written to: {out_file}")
    return out_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/gold_brands.csv")
    args = parser.parse_args()
    run_pipeline(args.input)