# Data sources

## 1. Curated Bangladesh prescription images

- URL: https://data.mendeley.com/datasets/k62rfd23kz/2
- Downloaded: 2026-09-25 by Esha
- Contents: 200 de-identified prescription images (printed and
  handwritten) in Bangla, English and mixed formats. Includes a
  `labels/` folder with YOLO-style bounding box coordinates for
  medicine-name regions, and a CSV listing image number and number of
  annotated medicine boxes per image.
- De-identification: patient and physician names, phone numbers,
  degrees, signatures, chamber details and registration numbers were
  removed by the publishers.
- Stored at: `data/raw/prescriptions_200/`
- Used in: Week 4 (crop extraction), Weeks 6-9 (evaluation set)
- Licence checked: ____________

OPEN ACTION (Week 4): spot-check 50 images for any remaining visible
identifiers. If any are found, exclude those images, record the
exclusion count here, and email the dataset authors.

---

## 2. RxHandBD, handwritten prescription word images

- URL: https://zenodo.org/records/18478741
- Mirror: https://data.mendeley.com/datasets/dsb5r6vskg/3
- DOI: 10.5281/zenodo.18478741
- Downloaded: 2026-09-25 by Esha
- Contents: 5,578 cropped handwritten word images, 128x128 RGB JPG.
  1,559 unique text entries covering generic names, brand names,
  dosage forms and clinical terms. Pre-split: 4,463 train with
  `train_labels.csv`, 1,115 test with `test_labels.csv`.
- Stored at: `data/raw/rxhandbd/`
- Used in: Weeks 4-5 (recognition training and evaluation)
- Owner from Week 4: Niyaz
- Licence checked: ____________

NOTE: use their existing 80/20 split. Do not make our own.

---

## 3. Doctor's Handwritten Prescription BD dataset

- URL: https://www.kaggle.com/datasets/mamun1113/doctors-handwritten-prescription-bd-dataset
- Downloaded: ____________
- Contents: word-segment images for 78 named Bangladeshi brands
  (Napa, Sergel, Monas, Azithrocin, Esoral, Maxpro, Fexo, Alatrol,
  Nexum and others).
- Stored at: `data/raw/bd_prescription_78/`
- Used in: Week 2 (source of the gold brand list)
- Licence checked: ____________

NOTE: the images are not needed yet. The 78 brand NAMES are what
Week 2 uses, hand-verified against dataset 4 and saved as
`data/processed/gold_brands.csv`.

---

## 4. Assorted Medicine Dataset of Bangladesh

- URL: https://www.kaggle.com/datasets/ahmedshahriarsakib/assorted-medicine-dataset-of-bangladesh
- Alternative source: https://data.mendeley.com/datasets/zhtvkny53n/1
- Downloaded: 2026-09-25 by Esha
- Contents: `medicine.csv` carries brand name, medicine type
  (allopathic or herbal), generic name, strength, manufacturer,
  package container with unit price, and package size. Separate files
  cover generics, indications, drug classes and manufacturers.
- Stored at: `data/external/catalogue_2026-09-25/`
- Used in: Weeks 1-3 and everywhere downstream
- Licence checked: ____________

### Inspection results (Esha, 2026-09-25)

- Total rows: 21,714
- Unique brand names: 13,934
- Unique generic names: approx. 1,700 to 1,800 (from Kaggle metadata,
  NOT counted directly: Excel was unavailable)
- Combination separators found: `&`, `+`, `,`

OPEN ACTION: recount unique generics exactly once `catalogue.py`
exists and replace the approximate figure. The thesis cannot cite an
approximation.

NOTE: the `&` separator was not in the original code template. The
SEPARATORS list must be `["+", "&", " and ", "/", ","]`.

NOTE: "Package Container" and "Package Size" need extra cleaning to
separate pack info from price. Price is not needed for this thesis,
so those columns can be dropped.

---

## 5. DDInter, drug-drug interactions

- Download page: https://ddinter.scbdd.com/download/
- DDInter 2.0: https://ddinter2.scbdd.com/
- Downloaded: 2026-09-26 by Niyaz
- Contents: 8 CSV files split by ATC category letter
  (A, B, D, H, L, P, R, V). Open access, no registration required.
- Stored at: `data/external/ddinter_2026-09-26/`
- Combined file: `data/interim/ddinter_combined.csv`
- Used in: Weeks 1-2 and everywhere downstream
- Licence and terms checked: ____________

### Inspection results (Niyaz, 2026-09-26)

- Column names: `DDInterID_A`, `Drug_A`, `DDInterID_B`, `Drug_B`,
  `Level`
- Severity column: `Level`, values in Title Case
- Severity distribution:
    Moderate  96,675
    Unknown   29,813
    Major     26,914
    Minor      6,833
- Rows before deduplication (8 files concatenated): 222,383
- Rows after deduplication: 160,235
- Unique drug names: 1,939
- Verified: every row is a unique unordered drug pair, and no pair
  appears twice with a conflicting severity.

The 62,148 dropped rows are pairs that appear in more than one ATC
category file. This is expected, not data loss.


CITATION NOTE: published papers describe DDInter as containing
approximately 0.24 million associations. Our snapshot yields 160,235
unique unordered pairs after deduplication. Cite our own figure with
the download date, not the published one.

---

## 6. DGDA registered drug lists

- URL: https://www.dgdagov.info
- Section: Information Center, registered drugs and registered
  imported drugs
- Downloaded: 2026-09-25 by Esha
- Contents: the official Bangladesh regulator's list of registered
  drug products.
- Stored at: `data/external/dgda_2026-09-25/`
- Used in: Week 3 (coverage check)

OPEN ACTION (Week 3): count how many DGDA-registered products are
absent from dataset 4. That number becomes a limitation paragraph:
our catalogue does not cover the full registered market.

---

# Human data collection

## Not required

- Nothing from any doctor
- Nothing from any patient
- No hospital, clinic or chamber access
- No prescriber permission

Every prescription analysed is already published, already
de-identified, and already licensed for research use.

## Required: one pharmacist, two hours, Week 8

100 prescription images from dataset 1, annotated by a pharmacy
student or pharmacist. A form with two columns: drugs they can read,
and interactions they identify. They record which reference they
checked against. We sit with them throughout. Co-authorship offered
on any resulting paper.

- Contact name: Md. Tanvir Haider Rabby 
- Institute: North South University
- Confirmed on: 29/09/2026

---

# Licence and redistribution

Raw datasets are NOT committed to this repository. They are linked
here instead. `.gitignore` excludes:

```
data/raw/*
data/external/*
data/interim/*
!**/.gitkeep
```
