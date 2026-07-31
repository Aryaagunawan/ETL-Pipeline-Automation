import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from utils.extract import extract
import pandas as pd

class TestExtractFunction(unittest.TestCase):

    @patch('utils.extract.requests.get')
    def test_valid_dataframe_returned(self, mock_get):
        # HTML contoh untuk pengujian
        simulated_html = """
        <div class="collection-card">
            <div class="product-title">Sample Product</div>
            <div class="price">$10</div>
            <img src="sample_image.jpg"/>
            <p>Rating: 4.5</p>
            <p>Colors Blue</p>
            <p>Size: L</p>
            <p>Gender: Female</p>
        </div>
        """

        # Simulasi respons dari requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = simulated_html
        mock_get.return_value = mock_response

        result_df = extract(max_pages=1)

        self.assertEqual(len(result_df), 1)
        self.assertEqual(result_df.loc[0, 'Title'], "Sample Product")
        self.assertEqual(result_df.loc[0, 'Price'], "$10")
        self.assertEqual(result_df.loc[0, 'Image URL'], "sample_image.jpg")
        self.assertEqual(result_df.loc[0, 'Rating'], "4.5")
        self.assertEqual(result_df.loc[0, 'Colors'], "Blue")
        self.assertEqual(result_df.loc[0, 'Size'], "L")
        self.assertEqual(result_df.loc[0, 'Gender'], "Female")
        self.assertIsInstance(result_df.loc[0, 'Timestamp'], pd.Timestamp)

    @patch('utils.extract.requests.get')
    def test_404_error_handling(self, mock_get):
        # Simulasi respons error 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result_df = extract(max_pages=1)
        self.assertTrue(result_df.empty)

if __name__ == '__main__':
    unittest.main()
