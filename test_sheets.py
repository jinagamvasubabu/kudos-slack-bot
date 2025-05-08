#!/usr/bin/env python3
"""
Test script for Google Sheets integration.
This script verifies your Google Sheets setup is working correctly.
"""

import os
import logging
from dotenv import load_dotenv
from sheets_integration import SheetsIntegration
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_sheets_integration():
    """Test Google Sheets integration by adding a test entry."""
    
    print("\n===== GOOGLE SHEETS INTEGRATION TEST =====\n")
    
    # Check environment variables
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID not set in environment variables.")
        print("   Please add it to your .env file.")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found at {creds_path}")
        print("   Please create a credentials.json file with your Google service account credentials.")
        return False
    
    print(f"✅ Environment variables look good!")
    print(f"   - Sheet ID: {sheet_id}")
    print(f"   - Credentials path: {creds_path}")
    
    # Initialize sheets integration
    print("\nInitializing Google Sheets integration...")
    sheets = SheetsIntegration()
    
    if not sheets.initialized:
        print("❌ Failed to initialize Google Sheets integration.")
        print("   Check your credentials and Google Sheet ID.")
        return False
    
    print("✅ Google Sheets integration initialized successfully!")
    
    # Create test data
    test_data = {
        'recipient_name': 'Test User',
        'recipient_id': 'U12345TEST',
        'recognition_type': 'Test Recognition (test_type)',
        'message': 'This is a test message to verify Google Sheets integration.',
        'sender_name': 'Test Sender',
        'sender_id': 'U67890TEST',
        'channel_id': 'C12345TEST'
    }
    
    # Log test recognition
    print("\nAttempting to write test data to sheet...")
    success = sheets.log_recognition(test_data)
    
    if success:
        print("✅ Test entry successfully added to Google Sheet!")
        print("   You should see a new row in your Google Sheet with test data.")
        print("\n🎉 Google Sheets integration is working properly!")
        return True
    else:
        print("❌ Failed to add test entry to Google Sheet.")
        print("   Please check your console logs for error details.")
        return False

if __name__ == "__main__":
    test_sheets_integration() 