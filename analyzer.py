
import pandas as pd


def analyze_dataset(df: pd.DataFrame) -> dict:
    """Find useful patterns in a dataset."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    results = {
        "numeric_correlations": {},
        "outlier_counts": {},
        "category_insights": {},
    }

    # 1. Find relationships between numerical columns
    numeric_df = df.select_dtypes(include="number")

    if len(numeric_df.columns) >= 2:
        correlations = numeric_df.corr().round(2)

        for column in correlations.columns:
            results["numeric_correlations"][column] = {
                other_column: float(value)
                for other_column, value in correlations[column].items()
                if other_column != column and pd.notna(value)
            }

    # 2. Estimate outliers using the IQR method
    for column in numeric_df.columns:
        values = numeric_df[column].dropna()

        if values.empty:
            results["outlier_counts"][column] = 0
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_count = int(
            ((values < lower_bound) | (values > upper_bound)).sum()
        )

        results["outlier_counts"][column] = outlier_count

    # 3. Summarize categories in text columns
    categorical_df = df.select_dtypes(
        include=["object", "category", "string"]
    )

    for column in categorical_df.columns:
        results["category_insights"][column] = (
            categorical_df[column]
            .value_counts()
            .head(5)
            .to_dict()
        )

    return results
