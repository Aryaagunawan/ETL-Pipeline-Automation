import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
from sqlalchemy import exc
from utils.load import (
    load_to_postgres,
    load_to_csv,
    load_to_google_sheets,
    load
)

class TestLoadFunctions(unittest.TestCase):
    def setUp(self):
        self.df_valid = pd.DataFrame({
            'id': [101, 102],
            'name': ['Alpha', 'Beta'],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02'])
        })
        self.df_empty = pd.DataFrame()
        self.dummy_db_url = "postgresql://testuser:testpass@localhost/testdb"
        self.dummy_csv = "dummy_output.csv"
        self.dummy_sheet_id = "dummy_google_sheet_id"

    # PostgreSQL
    @patch('utils.load.create_engine')
    def test_postgres_insert_success(self, mock_engine):
        mock_conn = MagicMock()
        mock_engine.return_value.begin.return_value.__enter__.return_value = mock_conn
        self.assertTrue(load_to_postgres(self.df_valid, self.dummy_db_url))

    @patch('utils.load.create_engine')
    def test_postgres_insert_fail_db_error(self, mock_engine):
        mock_engine.return_value.begin.side_effect = exc.SQLAlchemyError("Connection issue")
        self.assertFalse(load_to_postgres(self.df_valid, self.dummy_db_url))

    def test_postgres_insert_fail_empty_df(self):
        self.assertFalse(load_to_postgres(self.df_empty, self.dummy_db_url))

    # CSV
    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.DataFrame.to_csv')
    def test_csv_export_success(self, mock_to_csv, mock_file):
        self.assertTrue(load_to_csv(self.df_valid, self.dummy_csv))

    @patch('pandas.DataFrame.to_csv', side_effect=PermissionError("Access denied"))
    def test_csv_export_fail_io(self, mock_to_csv):
        self.assertFalse(load_to_csv(self.df_valid, self.dummy_csv))

    def test_csv_export_fail_empty_df(self):
        self.assertFalse(load_to_csv(self.df_empty, self.dummy_csv))

    # Google Sheets
    @patch('utils.load.gspread.authorize')
    @patch('utils.load.ServiceAccountCredentials.from_json_keyfile_name')
    def test_gsheets_upload_success(self, mock_creds, mock_auth):
        mock_client = MagicMock()
        mock_auth.return_value = mock_client
        mock_sheet = MagicMock()
        mock_client.open_by_key.return_value.get_worksheet.return_value = mock_sheet
        self.assertTrue(load_to_google_sheets(self.df_valid, self.dummy_sheet_id))

    @patch('utils.load.ServiceAccountCredentials.from_json_keyfile_name', 
           side_effect=FileNotFoundError("Keyfile missing"))
    def test_gsheets_upload_fail_creds(self, mock_creds):
        self.assertFalse(load_to_google_sheets(self.df_valid, self.dummy_sheet_id))

    @patch('utils.load.gspread.authorize')
    @patch('utils.load.ServiceAccountCredentials.from_json_keyfile_name')
    def test_gsheets_upload_fail_exception(self, mock_creds, mock_auth):
        mock_auth.return_value.open_by_key.side_effect = Exception("GSheet error")
        self.assertFalse(load_to_google_sheets(self.df_valid, self.dummy_sheet_id))

    def test_gsheets_upload_fail_empty_df(self):
        self.assertFalse(load_to_google_sheets(self.df_empty, self.dummy_sheet_id))

    # Combined load
    @patch('utils.load.load_to_postgres', return_value=True)
    @patch('utils.load.load_to_csv', return_value=True)
    @patch('utils.load.load_to_google_sheets', return_value=True)
    def test_full_load_all_success(self, mock_gsheet, mock_csv, mock_pg):
        result = load(self.df_valid, self.dummy_db_url, self.dummy_csv, self.dummy_sheet_id)
        self.assertTrue(all(result.values()))

    @patch('utils.load.load_to_postgres', return_value=False)
    @patch('utils.load.load_to_csv', return_value=True)
    @patch('utils.load.load_to_google_sheets', return_value=False)
    def test_full_load_partial_success(self, mock_gsheet, mock_csv, mock_pg):
        result = load(self.df_valid, self.dummy_db_url, self.dummy_csv, self.dummy_sheet_id)
        self.assertEqual(result, {
            "postgres": False,
            "csv": True,
            "google_sheets": False
        })

    def test_full_load_invalid_input_type(self):
        result = load("invalid type", self.dummy_db_url, self.dummy_csv, self.dummy_sheet_id)
        self.assertFalse(any(result.values()))

if __name__ == '__main__':
    unittest.main()
