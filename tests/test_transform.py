import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd
import numpy as np
from utils.transform import transform, clean_rating

class TestTransformFunctions(unittest.TestCase):

    def setUp(self):
        # Contoh data yang akan digunakan untuk pengujian
        self.data = pd.DataFrame({
            "Title": ["T-shirt", "Unknown", "Shirt"],
            "Rating": ["4.5", "Invalid", "Not Available"],
            "Price": ["$10.00", "Unavailable", "$20.00"],
            "Colors": ["Colors 3", "Colors 2", "Colors 1"],
            "Size": ["Medium", "Large", "Unknown"],
            "Gender": ["Male", "Female", "Unisex"],
            "Timestamp": ["2023-01-01", "Invalid Date", "2023-05-02"]
        })

    def test_clean_rating_various_inputs(self):
        test_cases = {
            "4.5": 4.5,
            "Rating: 3.2": 3.2,
            "4.2 stars": 4.2,
            "Invalid": np.nan,
            None: np.nan
        }
        for input_str, expected in test_cases.items():
            result = clean_rating(input_str)
            if pd.isna(expected):
                self.assertTrue(pd.isna(result))
            else:
                self.assertAlmostEqual(result, expected)

    def test_transform_valid_row_output(self):
        df_transformed = transform(self.data)
        self.assertEqual(df_transformed.shape[0], 1)

        row = df_transformed.iloc[0]
        self.assertEqual(row.Title, 't-shirt')
        self.assertEqual(row.Size, 'M')
        self.assertEqual(row.Gender, 'Men')
        self.assertEqual(row.Colors, 3)
        self.assertAlmostEqual(row.Price, 160000.0)
        self.assertAlmostEqual(row.Rating, 4.5)
        self.assertTrue(pd.api.types.is_datetime64_dtype(df_transformed.Timestamp))

    def test_transform_raises_on_missing_column(self):
        data_missing = self.data.drop(columns=['Rating'])
        with self.assertRaises(KeyError):
            transform(data_missing)

    def test_transform_rejects_non_dataframe(self):
        with self.assertRaises(ValueError):
            transform("invalid input")

    def test_transform_returns_empty_for_none(self):
        self.assertTrue(transform(None).empty)

if __name__ == '__main__':
    unittest.main()
