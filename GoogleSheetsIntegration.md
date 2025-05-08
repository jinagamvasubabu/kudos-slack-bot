# Google Sheets Integration (Optional)

The Kudos Slack bot can automatically log all recognitions to a Google Sheet, providing a centralized audit trail of all kudos exchanged in your workspace.

## What Gets Logged 📊

Each recognition logs the following information:
- Timestamp
- Recipient name and ID
- Recognition type
- Message content
- Sender name and ID
- Channel ID

## Setup Instructions 🛠️

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" at the top right
3. Give your project a name (e.g., "Kudos Bot") and click "Create"
4. Select your new project from the dropdown menu

### 2. Enable Required APIs

1. Go to "APIs & Services" > "Library"
2. Search for and enable these two APIs:
   - "Google Sheets API"
   - "Google Drive API"
   - Click on each, then click "Enable"

### 3. Create a Service Account

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter service account details:
   - Name: "kudos-bot"
   - ID: will be auto-generated
   - Description: "Service account for Kudos Slack bot"
4. Click "Create and Continue"
5. For Role, select "Basic" > "Editor"
6. Click "Continue" then "Done"

### 4. Create and Download Credentials

1. Find your new service account in the list and click on it
2. Go to the "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" and click "Create"
5. The key file will download automatically
6. Rename the file to `credentials.json` and move it to your project directory

### 5. Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/) and create a new spreadsheet
2. Open the downloaded `credentials.json` file and copy the `client_email` value
3. Click "Share" in your Google Sheet
4. Paste the client email and give it "Editor" access
5. Make sure "Notify people" is unchecked
6. Click "Share"

### 6. Get Your Spreadsheet ID

1. Look at the URL of your Google Sheet
2. The spreadsheet ID is the long string of characters between `/d/` and `/edit`
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE/edit#gid=0
   ```
3. Copy this ID

### 7. Update Your Environment Variables

Add these variables to your `.env` file:

```
GOOGLE_SHEET_ID=your-spreadsheet-id
GOOGLE_CREDENTIALS_PATH=credentials.json
```

### 8. Configure Sheets Integration (Optional)

You can customize the Google Sheets integration by editing `config.py`:

```python
SHEETS_CONFIG = {
    # Enable/disable Google Sheets integration
    "enabled": True,
    
    # Default path to credentials file (can be overridden in .env)
    "default_credentials_path": "credentials.json",
    
    # Sheet headers configuration
    "headers": [
        "Timestamp", 
        "Recipient", 
        "Recipient ID",
        "Recognition Type",
        "Message", 
        "Sender", 
        "Sender ID", 
        "Channel ID"
    ],
    
    # Auto-create headers if sheet is empty
    "auto_create_headers": True,
    
    # Time format for logging
    "timestamp_format": "%Y-%m-%d %H:%M:%S"
}
```

## Testing the Integration 🧪

A test script is included to verify your Google Sheets integration is working correctly:

```bash
python test_sheets.py
```

If successful, you'll see "Successfully wrote test data to sheet" and a test entry will appear in your Google Sheet.

## Troubleshooting 🔍

### Common Issues

1. **Sheets integration not initialized**
   - Ensure `GOOGLE_SHEET_ID` is set correctly in your `.env` file
   - Verify `credentials.json` exists in your project directory
   - Make sure Google Sheets API is enabled in your Google Cloud project

2. **Permission errors**
   - Check that you shared the sheet with the correct service account email
   - Verify the service account has "Editor" access to the sheet

3. **API not enabled**
   - Make sure both Google Sheets API and Google Drive API are enabled

4. **Quota limits**
   - Google has API usage limits that may affect the integration
   - If you hit limits, consider upgrading your Google Cloud project

## Advanced Debugging 🔧

For advanced debugging of Google Sheets integration issues:

```bash
# Create debugging file
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from sheets_integration import SheetsIntegration
sheets = SheetsIntegration()
print(f'Initialized: {sheets.initialized}')
if sheets.initialized:
    test_data = {
        'recipient_name': 'Test User',
        'recipient_id': 'TEST123',
        'recognition_type': 'Test',
        'message': 'Testing sheets integration',
        'sender_name': 'Debug Tool',
        'sender_id': 'DEBUG',
        'channel_id': 'DEBUG'
    }
    result = sheets.log_recognition(test_data)
    print(f'Result: {result}')
"
```

This will show detailed logs about the Sheets integration process. 