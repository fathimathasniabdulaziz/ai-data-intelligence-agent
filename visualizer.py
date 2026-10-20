
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def generate_charts(
    df: pd.DataFrame,
    output_dir: str = "charts"
) -> list[str]:
    """Generate charts automatically from a dataset."""

    if df.empty:
        raise ValueError("Cannot generate charts from an empty dataset.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # Chart 1: Histograms for numerical columns
    numeric_df = df.select_dtypes(include="number")

    for column in numeric_df.columns[:4]:
        values = numeric_df[column].dropna()

        if values.empty:
            continue

        plt.figure(figsize=(8, 5))
        plt.hist(values, bins=10, edgecolor="black")
        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.tight_layout()

        file_path = output_path / f"{column}_histogram.png"
        plt.savefig(file_path)
        plt.close()

        generated_files.append(str(file_path))

    # Chart 2: Bar charts for text/category columns
    categorical_df = df.select_dtypes(
        include=["object", "category", "string"]
    )

    for column in categorical_df.columns[:3]:
        counts = categorical_df[column].value_counts().head(10)

        if counts.empty:
            continue

        plt.figure(figsize=(8, 5))
        counts.plot(kind="bar")
        plt.title(f"Top Categories in {column}")
        plt.xlabel(column)
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        file_path = output_path / f"{column}_bar_chart.png"
        plt.savefig(file_path)
        plt.close()

        generated_files.append(str(file_path))

    return generated_files
