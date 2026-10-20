
import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """Summarize the structure and quality of a dataset."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    missing_values = {
        column: int(count)
        for column, count in df.isnull().sum().items()
        if count > 0
    }

    return {
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "missing_values": missing_values,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_statistics": df[numeric_columns].describe().round(2).to_dict(),
    }
