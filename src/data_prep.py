import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    print(data.shape)
    return data



def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning based on business logic:
    exposure must be > 0
    claimNB must be >= 0 
    convert key numeric and categorical columns to appropriate types
    """

    df = df.copy()
    numeric_cols = ["ClaimNb", "Exposure", "VehPower", "VehAge", "DrivAge", "BonusMalus", "Density"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    cat_cols = ["Area", "VehBrand", "VehGas", "Region"]

    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    print("Rows before cleaning:", len(df))

    df = df[df["Exposure"] > 0]
    df = df[df["ClaimNb"] >= 0]

    df["ClaimNb"] = df["ClaimNb"].round().astype(int)

    print("Rows after cleaning:", len(df))

    return df


def add_claim_freq(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add claimFreq = claimNb / Exposure (per policy-year)
    """

    df = df.copy()
    df["ClaimFreq"] = df["ClaimNb"] / df["Exposure"]
    return df

def summarize_data(df: pd.DataFrame):

    """
    -dataframe info and data types
    -null value percentages
    -numerical column statistics
    -simple IQR-based outlier detection
    """

    print(df.info())

    print("\n Percentage of null values per column:")
    print((df.isna().mean() * 100).sort_values(ascending=False))


    numeric_cols = ["ClaimNb", "Exposure", "VehPower", "VehAge", "DrivAge", "BonusMalus", "Density"]
    numeric_cols = [c for c in numeric_cols if c in df.columns]

    print("Statistics for numeric columns:")
    print(df[numeric_cols].describe(percentiles=[0.01, 0.05, 0.95, 0.99]).T)

    print("Potential outliers(IQR):")
    for col in numeric_cols:
        s = df[col].dropna()
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = ((s < lower) | (s > upper)).mean() * 100
        print(f" {col} - {outliers:.2f}% flagged as potential outliers")

if __name__ == "__main__":

    data = load_data("data/freMTPL2freq.csv")
    data_clean = basic_clean(data)
    data_clean = add_claim_freq(data_clean)

    summarize_data(data_clean)
    print(data_clean.head())