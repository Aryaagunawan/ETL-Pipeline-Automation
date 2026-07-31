from typing import Dict
import pandas as pd
import traceback
from sqlalchemy import create_engine, exc
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import GSpreadException
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_to_postgres(df: pd.DataFrame, db_url: str) -> bool:
    """
    Load data to PostgreSQL database.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Empty or invalid DataFrame provided")
        return False
        
    try:
        engine = create_engine(db_url)
        with engine.begin() as connection: 
            df.to_sql(
                "products", 
                connection,
                index=False,
                if_exists="replace"
            )
        return True
    except exc.SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def load_to_csv(df: pd.DataFrame, csv_file_path: str) -> bool:
    """
    Save data to CSV.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Empty or invalid DataFrame provided")
        return False
        
    try:
        df.to_csv(csv_file_path, index=False)
        return True
    except (IOError, PermissionError) as e:
        logger.error(f"File system error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def load_to_google_sheets(df: pd.DataFrame, spreadsheet_id: str) -> bool:
    """
    Load data to Google Sheets using spreadsheet ID
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.warning("Empty or invalid DataFrame provided")
        return False

    try:
        # 1. Convert data
        df = df.copy()
        for col in df.select_dtypes(include=['datetime64[ns]']).columns:
            df[col] = df[col].apply(lambda x: x.isoformat() if pd.notna(x) else '')

        # 2. Setup credentials
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "google-sheets-api.json", scope)
        client = gspread.authorize(creds)

        # 3. Access spreadsheet by ID
        spreadsheet = client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.get_worksheet(0)
        
        # 4. Update data
        sheet.clear()
        data = [df.columns.tolist()] + df.fillna('').astype(str).values.tolist()
        sheet.update('A1', data)
        
        logger.info(f"Successfully updated Google Sheets: {spreadsheet.title}")
        return True

    except gspread.exceptions.APIError as e:
        logger.error(f"Google API Error: {e.response.text}")
        return False
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error(f"Spreadsheet with ID {spreadsheet_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error updating Google Sheets: {str(e)}")
        traceback.print_exc()
        return False

def load(df: pd.DataFrame, db_url: str, csv_file_path: str, spreadsheet_id: str) -> Dict[str, bool]:
    """
    Load data to all destinations.
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("Input is not a DataFrame")
        return {
            "postgres": False,
            "csv": False,
            "google_sheets": False
        }
    
    return {
        "postgres": load_to_postgres(df, db_url),
        "csv": load_to_csv(df, csv_file_path),
        "google_sheets": load_to_google_sheets(df, spreadsheet_id)
    }