# RxSafe: Medication Error Propagation & Safety Screening Framework

RxSafe is a research framework and pipeline designed for detecting drug-drug interactions (DDIs), evaluating medication safety, and modeling error propagation from prescription image recognition (OCR / VLMs) through brand name normalization to safety screening.

## 📁 Repository Structure

```text
rxsafe/
├── data/
│   ├── raw/         # Downloaded datasets, never edited
│   ├── interim/     # Cleaned intermediate files
│   ├── processed/   # Final analysis-ready files
│   └── external/    # Catalogue snapshot, DDInter snapshot
├── src/
│   ├── catalogue.py # Load and clean the product catalogue
│   ├── normalize.py # Brand string -> generic -> class normalization
│   ├── ddi.py       # Interaction lookup engine
│   ├── screen.py    # The three safety detectors
│   ├── inject.py    # Controlled error injection pipeline
│   ├── recognize.py # OCR and VLM wrappers
│   ├── metrics.py   # Recall, precision, severity-weighted recall
│   └── experiment.py# Propagation and decomposition runs
├── notebooks/       # Exploration notebooks (never the source of a final result)
├── results/
│   ├── figures/     # Generated plots and figures
│   ├── tables/      # Exported result tables
│   └── runs/        # Run outputs, partitioned by date and random seed
├── docs/
│   ├── log/         # Daily research logs (YYYY-MM-DD.md)
│   ├── meetings/    # Wednesday meeting minutes
│   └── thesis/      # Chapter drafts and documentation
├── tests/           # Unit tests and validation suite
├── README.md        # Project overview and setup instructions
└── requirements.txt # Python dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+

### Installation

```bash
# Clone the repository
git clone https://github.com/theniyazkhan/rxsafe.git
cd rxsafe

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🧪 Quick Run

Run test suite to verify setup:
```bash
pytest
```

Run the safety screening pipeline on the gold standard brands dataset:
```bash
python -m src.experiment --input data/processed/gold_brands.csv
```
