import os
import sys
import argparse
import pandas as pd
import yaml
from datetime import datetime
from src.catalogue import load_catalogue, expand_catalogue
from src.normalize import build_index, normalize_one
from src.ddi import load_ddi
from src.screen import check_interactions


def run_pipeline(input_path: str, mode: str):
    if not os.path.exists("config.yaml"):
        print("Error: config.yaml not found.")
        sys.exit(1)
        
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        
    cat_path = config["paths"]["catalogue"]
    ddi_path = config["paths"]["ddinter"]
    threshold = config["normalize"]["threshold"]
    
    if not os.path.exists(cat_path):
        print(f"Error: Catalogue file expected at '{cat_path}' does not exist.")
        sys.exit(1)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("results", "runs", run_id)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Load Knowledge Layer
    cat_raw = load_catalogue(cat_path)
    cat = expand_catalogue(cat_raw)
    brand_list = build_index(cat)
    
    # 2. Read input file
    rx_df = pd.read_csv(input_path)
    
    if mode == "normalize":
        results = []
        total = len(rx_df)
        correct = 0
        abstained = 0
        incorrect = 0
        
        for _, row in rx_df.iterrows():
            brand = str(row["brand"])
            expected = str(row["generic"]).lower().strip()
            
            norm = normalize_one(brand, brand_list, cat, threshold)
            matched = norm["matched_generic"]
            is_abstained = norm["abstained"]
            score = norm["score"]
            
            is_correct = False
            if not is_abstained and matched:
                matched_joined = " + ".join(sorted(matched))
                expected_joined = " + ".join(sorted([x.strip() for x in expected.split("+")]))
                is_correct = (matched_joined == expected_joined)
                
            if is_correct:
                correct += 1
            elif is_abstained:
                abstained += 1
            else:
                incorrect += 1
                
            results.append({
                "brand": brand,
                "expected_generic": expected,
                "matched_generic": matched,
                "score": score,
                "abstained": is_abstained,
                "correct": is_correct
            })
            
        out_file = os.path.join(out_dir, "normalization.csv")
        pd.DataFrame(results).to_csv(out_file, index=False)
        print(f"Total rows: {total}")
        print(f"Resolved correctly: {correct} ({(correct/total)*100:.1f}%)")
        print(f"Abstained: {abstained} ({(abstained/total)*100:.1f}%)")
        print(f"Resolved incorrectly: {incorrect} ({(incorrect/total)*100:.1f}%)")
        return out_file
        
    elif mode == "screen":
        if "rx_id" not in rx_df.columns or "brand_string" not in rx_df.columns:
            print("No prescription file supplied. Screening mode requires real multi-drug prescriptions.")
            sys.exit(0)
            
        if not os.path.exists(ddi_path):
            print(f"Error: DDInter file expected at '{ddi_path}' does not exist.")
            sys.exit(1)
            
        ddi_table = load_ddi(ddi_path)
        all_alerts = []
        for rx_id, group in rx_df.groupby("rx_id"):
            generics = []
            for raw_brand in group["brand_string"]:
                norm = normalize_one(raw_brand, brand_list, cat, threshold)
                if not norm["abstained"] and norm["matched_generic"]:
                    generics.extend(norm["matched_generic"])
            
            rx_alerts = check_interactions(str(rx_id), generics, ddi_table)
            for a in rx_alerts:
                all_alerts.append(a)

        out_file = os.path.join(out_dir, "alerts.csv")
        pd.DataFrame(all_alerts).to_csv(out_file, index=False)
        print(f"Run completed successfully. Alerts written to: {out_file}")
        return out_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--mode", choices=["normalize", "screen"], required=True)
    args = parser.parse_args()
    
    if args.input is None:
        if args.mode == "normalize":
            if os.path.exists("config.yaml"):
                with open("config.yaml", "r") as f:
                    config = yaml.safe_load(f)
                args.input = config["paths"]["gold_brands"]
            else:
                args.input = "data/processed/gold_brands.csv"
        else:
            print("No prescription file supplied. Screening mode requires real multi-drug prescriptions.")
            sys.exit(0)
            
    run_pipeline(args.input, args.mode)