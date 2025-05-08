"""
Google Sheets integration module for the Kudos bot.
This module handles saving recognition data to a Google Sheet for auditing purposes.
"""

import os
import json
import logging
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEETS_CONFIG

logger = logging.getLogger(__name__)

# Define the scope
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

class SheetsIntegration:
    def __init__(self):
        """Initialize the Google Sheets integration."""
        self.client = None
        self.sheet = None
        self.initialized = False
        
        # Check if Google Sheets integration is enabled in config
        if not SHEETS_CONFIG.get("enabled", True):
            logger.info("Google Sheets integration is disabled in config.py")
            return
        
        # Get credentials path (env var takes precedence over config)
        self.credentials_path = os.environ.get(
            "GOOGLE_CREDENTIALS_PATH", 
            SHEETS_CONFIG.get("default_credentials_path", "credentials.json")
        )
        
        # Get spreadsheet ID from environment
        self.spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID")
        
        if not self.spreadsheet_id:
            logger.warning("GOOGLE_SHEET_ID not set in environment variables. Google Sheets integration disabled.")
            return
            
        try:
            # Initialize the client
            self._initialize_client()
        except Exception as e:
            logger.error(f"Error initializing Google Sheets client: {e}")
    
    def _initialize_client(self):
        """Initialize the Google Sheets client."""
        try:
            # If credentials file exists, authenticate
            if os.path.exists(self.credentials_path):
                logger.info(f"Found credentials file at {self.credentials_path}")
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_path, SCOPE
                )
                self.client = gspread.authorize(credentials)
                logger.info(f"Successfully authorized with Google using credentials")
                
                # Try to open the spreadsheet
                logger.info(f"Attempting to open spreadsheet with ID: {self.spreadsheet_id}")
                self.sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
                logger.info(f"Successfully opened spreadsheet")
                
                # Check if the sheet has headers, if not add them
                auto_create_headers = SHEETS_CONFIG.get("auto_create_headers", True)
                if auto_create_headers and not self.sheet.row_values(1):
                    headers = SHEETS_CONFIG.get("headers", [
                        "Timestamp", "Recipient", "Recipient ID", "Recognition Type",
                        "Message", "Sender", "Sender ID", "Channel ID"
                    ])
                    logger.info(f"Adding headers to sheet: {headers}")
                    self.sheet.append_row(headers)
                
                self.initialized = True
                logger.info("Google Sheets integration initialized successfully.")
            else:
                logger.warning(f"Credentials file not found at {self.credentials_path}")
                logger.warning(f"Current working directory: {os.getcwd()}")
                logger.warning(f"Files in directory: {os.listdir('.')}")
                logger.warning("Google Sheets integration disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            logger.exception("Detailed error information:")
    
    def log_recognition(self, recognition_data):
        """
        Log a recognition to Google Sheets.
        
        Args:
            recognition_data (dict): A dictionary containing recognition data.
                Example:
                {
                    'recipient_name': 'John Doe',
                    'recipient_id': 'U12345',
                    'recognition_type': 'silent_soldier',
                    'message': 'Great job on the project!',
                    'sender_name': 'Jane Smith',
                    'sender_id': 'U67890',
                    'channel_id': 'C12345'
                }
        
        Returns:
            bool: True if logging was successful, False otherwise.
        """
        if not self.initialized:
            logger.warning("Google Sheets integration not initialized. Skipping logging.")
            logger.warning(f"Spreadsheet ID: {self.spreadsheet_id}")
            logger.warning(f"Credentials Path: {self.credentials_path}")
            logger.warning(f"SHEETS_CONFIG enabled: {SHEETS_CONFIG.get('enabled', True)}")
            logger.warning(f"Credentials file exists: {os.path.exists(self.credentials_path)}")
            return False
        
        try:
            # Format timestamp using format from config
            timestamp_format = SHEETS_CONFIG.get("timestamp_format", "%Y-%m-%d %H:%M:%S")
            timestamp = datetime.now().strftime(timestamp_format)
            
            # Get headers from config to determine column order
            headers = SHEETS_CONFIG.get("headers", [
                "Timestamp", "Recipient", "Recipient ID", "Recognition Type",
                "Message", "Sender", "Sender ID", "Channel ID"
            ])
            
            # Create row data dictionary using headers
            row_data = {
                "Timestamp": timestamp,
                "Recipient": recognition_data.get('recipient_name', 'Unknown'),
                "Recipient ID": recognition_data.get('recipient_id', ''),
                "Recognition Type": recognition_data.get('recognition_type', ''),
                "Message": recognition_data.get('message', ''),
                "Sender": recognition_data.get('sender_name', 'Unknown'),
                "Sender ID": recognition_data.get('sender_id', ''),
                "Channel ID": recognition_data.get('channel_id', '')
            }
            
            # Prepare row in the correct order based on headers
            row = [row_data.get(header, '') for header in headers]
            
            # Append row to sheet
            logger.info(f"Appending row to sheet: {row}")
            self.sheet.append_row(row)
            logger.info(f"Recognition successfully logged to Google Sheets: {recognition_data.get('recipient_name')} - {recognition_data.get('recognition_type')}")
            return True
        except Exception as e:
            logger.error(f"Error logging recognition to Google Sheets: {e}")
            logger.exception("Detailed error information:")
            return False

# Create a singleton instance
sheets = SheetsIntegration() 