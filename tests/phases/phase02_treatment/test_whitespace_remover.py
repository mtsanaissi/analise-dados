import os
import shutil
import pandas as pd
from src.phases.phase02_treatment.phase02_orchestrator import run_treatment_phase

def test_strip_whitespace():
    # Setup
    test_data_dir = "tests/data/strip_whitespace_test"
    os.makedirs(test_data_dir, exist_ok=True)

    source_file = "tests/data/whitespace_test.csv"
    test_file = os.path.join(test_data_dir, "whitespace_test.csv")
    shutil.copy(source_file, test_file)

    # Run the strip whitespace operation
    run_treatment_phase(test_data_dir, ["--strip-whitespace"])

    # Read the processed file
    df = pd.read_csv(test_file, sep=';', dtype=str)

    # Assertions
    # Check column names
    expected_columns = ["Nome  ", "  Idade", "Data "]
    assert list(df.columns) == expected_columns

    # Check values
    assert df.iloc[0, 0] == "João"
    assert df.iloc[0, 1] == "25"
    assert df.iloc[0, 2] == "2023-01-01"
    assert df.iloc[1, 0] == "Maria"
    assert df.iloc[1, 1] == "30"
    assert df.iloc[1, 2] == "2023-02-01"
    assert df.iloc[2, 0] == "José"
    assert df.iloc[2, 1] == "35"
    assert df.iloc[2, 2] == "2023-03-01"

    # Teardown
    shutil.rmtree(test_data_dir)

    # Remove backup directory
    for item in os.listdir("."):
        if item.startswith("fad-bkp-treatment-"):
            shutil.rmtree(item)
