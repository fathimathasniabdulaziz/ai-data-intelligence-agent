import pandas as pd
from pathlib import Path


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a CSV or Excel dataset.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)

    elif path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)

    else:
        raise ValueError(
            "Unsupported file format. Please use CSV or Excel."
        )

    return df