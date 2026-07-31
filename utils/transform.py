import pandas as pd
import numpy as np
import re

def clean_rating(value):
    try:
        match = re.search(r"\d+(\.\d+)?", str(value))  # Convert to string to avoid errors
        if match:
            return float(match.group())
        else:
            return np.nan
    except Exception as e:
        return np.nan

def transform(raw_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Transform raw data by cleaning and converting columns to appropriate formats.
    """
    # Input validation
    if raw_df is None:
        return pd.DataFrame()

    if not isinstance(raw_df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    required_columns = [
        "Title", "Rating", "Price", "Colors", "Size", "Gender", "Timestamp"
    ]
    missing_columns = [col for col in required_columns if col not in raw_df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {', '.join(missing_columns)}")

    try:
        df = raw_df.copy()

        # Clean Title
        df["Title"] = df["Title"].str.lower()
        df.loc[df["Title"].str.contains("unknown", na=False), "Title"] = pd.NA

        # Clean Rating
        df["Rating"] = df["Rating"].str.lower()
        df.loc[df["Rating"].str.contains("invalid|not", na=False), "Rating"] = pd.NA

        # Clean Price
        df["Price"] = df["Price"].str.lower()
        df.loc[df["Price"].str.contains("unavailable", na=False), "Price"] = pd.NA

        # Drop missing values
        df = df.dropna()

        # Transform Rating
        df["Rating"] = df["Rating"].apply(clean_rating)

        # Transform Price to float, remove dollar sign, convert to IDR
        df["Price"] = (
            df["Price"]
            .str.replace(r"[^\d.]", "", regex=True)  # Remove any non-numeric characters
            .astype(float) * 16000
        )

        # Clean Colors
        df["Colors"] = df["Colors"].str.extract(r"(\d+)")[0]
        df["Colors"] = pd.to_numeric(df["Colors"], errors='coerce')  # Convert to numeric, handle errors

        # Clean Size (assuming 'S', 'M', 'L', 'XL', 'XXL' are common values)
        size_map = {
            'small': 'S', 'medium': 'M', 'large': 'L', 'xlarge': 'XL', 'xxlarge': 'XXL',
            's': 'S', 'm': 'M', 'l': 'L', 'xl': 'XL', 'xxl': 'XXL'
        }
        df["Size"] = df["Size"].str.lower().map(size_map).fillna('Unknown')  # Map sizes to proper values
        df["Size"] = df["Size"].replace("unknown", "Unknown")  # Replace any remaining "unknown"

        # Clean Gender (assuming 'Male', 'Female', 'Unisex' are common values)
        gender_map = {
            'male': 'Men', 'female': 'Women', 'unisex': 'Unisex',
            'men': 'Men', 'women': 'Women', 'unisex': 'Unisex'
        }
        df["Gender"] = df["Gender"].str.lower().map(gender_map).fillna('Unknown')  # Map gender values

        # Timestamp to datetime
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')  # Handle invalid date formats

        return df

    except Exception as e:
        raise Exception(f"An error occurred during data transformation: {e}") from e

