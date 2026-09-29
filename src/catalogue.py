import os
import pandas as pd

import yaml

SEPARATORS = ["+", "&", " and ", "/", ","]

def clean_name(s):
    if not isinstance(s, str):
        return ""
    s = s.lower().strip()
    for ch in ".,()[]/-+&":
        s = s.replace(ch, " ")
    return " ".join(s.split())

def load_catalogue(path):
    print("Loading catalogue from:", path)
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from {path}")
    
    brand_col = "brand name" if "brand name" in df.columns else ("brand" if "brand" in df.columns else None)
    gen_col = "generic" if "generic" in df.columns else None
    
    if not brand_col or not gen_col:
        raise ValueError(f"Columns not found. Available columns: {list(df.columns)}")
        
    df["generic"] = df[gen_col]
    df["brand_clean"] = df[brand_col].apply(clean_name)
    df["generic_clean"] = df[gen_col].apply(clean_name)
    df = df[df["brand_clean"] != ""]
    df = df.drop_duplicates(subset=["brand_clean", "generic_clean"])
    return df

def split_combo(generic_text):
    parts = [generic_text]
    for sep in SEPARATORS:
        new_parts = []
        for p in parts:
            new_parts.extend(p.split(sep))
        parts = new_parts
    return [clean_name(p) for p in parts if clean_name(p)]

def expand_catalogue(df, generic_col="generic"):
    rows = []
    for i, r in df.iterrows():
        components = split_combo(str(r[generic_col]))
        for c in components:
            rows.append({
                "brand_clean": r["brand_clean"],
                "generic_clean": c,
                "combo_id": i,
                "combo_size": len(components),
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if not os.path.exists("config.yaml"):
        print("Error: config.yaml not found.")
        sys.exit(1)
    
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    if args.sample:
        raw_path = config["paths"]["catalogue_sample"]
    else:
        raw_path = config["paths"]["catalogue"]
    if not os.path.exists(raw_path):
        print(f"Error: Catalogue file expected at '{raw_path}' does not exist.")
        sys.exit(1)

    out_dir = "data/interim"
    os.makedirs(out_dir, exist_ok=True)
    
    cat_df = load_catalogue(raw_path)
    expanded_df = expand_catalogue(cat_df)
    
    out_path = os.path.join(out_dir, "catalogue.csv")
    expanded_df.to_csv(out_path, index=False)
    print(f"Saved cleaned catalogue to {out_path} with {len(expanded_df)} rows.")