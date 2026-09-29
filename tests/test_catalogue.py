from src.catalogue import split_combo

def test_combo_splits_on_plus():
    assert split_combo("Paracetamol + Caffeine") == ["paracetamol", "caffeine"]

def test_combo_splits_on_ampersand():
    assert split_combo("Magnesium Hydroxide & Aluminium Hydroxide") == [
        "magnesium hydroxide", "aluminium hydroxide"]

def test_single_drug_stays_single():
    assert split_combo("Metronidazole") == ["metronidazole"]

def test_spaces_preserved():
    from src.catalogue import clean_name
    assert clean_name("Napa Extra") == "napa extra"
