# Kudos Slack Bot 🎉

A Slack bot that allows team members to give kudos to their colleagues with customizable recognition types and emojis.

<img src="kudos_bot.png" alt="Kudos Bot Screenshot" width="600"/>

## Features ✨

- 🔌 **Socket Mode Support**: No public URL needed, works behind firewalls
- 👥 **User-Friendly Interface**: Clean modal with dropdowns for easy kudos giving
- 🎨 **Customizable Recognition Types**: Easily configure recognition categories and emojis
- 💬 **Rich Text Support**: Use emojis and @mentions in your kudos messages
- 📊 **Google Sheets Integration** (Optional): Audit all recognitions ([setup instructions](GoogleSheetsIntegration.md))

## Quick Start 🚀

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kudos-slack-bot
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file**
   ```
   # Required Slack Tokens
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_SIGNING_SECRET=your-signing-secret
   SLACK_APP_TOKEN=xapp-your-app-level-token
   
   # Optional Google Sheets Integration
   # GOOGLE_SHEET_ID=your-spreadsheet-id
   # GOOGLE_CREDENTIALS_PATH=credentials.json
   ```

5. **Start the bot**
   ```bash
   python app.py
   ```

## Slack App Setup 🔧

### 1. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" > "From scratch"
3. Enter app name and select your workspace

### 2. Configure App Settings

1. **Enable Socket Mode**
   - Go to "Socket Mode" and enable it
   - Generate an app-level token with `connections:write` scope
   - Add this as `SLACK_APP_TOKEN` in your `.env` file

2. **Set Up Bot Permissions**
   - Go to "OAuth & Permissions" > "Scopes"
   - Add bot token scopes:
     - `chat:write` - Send messages
     - `commands` - Use slash commands
     - `users:read` - Get user information
     - `app_mentions:read` - Respond to @mentions
     - `im:history` - Access DM history
     - `channels:history` - Access channel history

3. **Create Slash Command**
   - Go to "Slash Commands" > "Create New Command"
   - Command: `/kudos`
   - Description: "Give kudos to a team member"
   - Usage hint: `[@user] [message]`

4. **Enable Event Subscriptions**
   - Go to "Event Subscriptions" and enable events
   - Subscribe to bot events:
     - `message.channels`
     - `message.im`

5. **Install the App**
   - Go to "Install App" and install to your workspace
   - Copy the bot token to `SLACK_BOT_TOKEN` in your `.env` file

## Usage 📝

1. In any Slack channel, type `/kudos`
2. Select a team member from the dropdown
3. Choose a recognition type
4. Write your kudos message (supports emojis and @mentions)
5. Click "Send Kudos"

## Customization ⚙️

### Recognition Types

Edit `config.py` to customize recognition types:

```python
RECOGNITION_TYPES = {
    "silent_soldier": {
        "title": "Silent Soldier",
        "emoji": "🥷"
    },
    "helping_hand": {
        "title": "Helping Hand",
        "emoji": "🤝"
    },
    # Add more types here...
}
```

## Optional Features 🌟

- **Google Sheets Integration**: Track all recognitions in a spreadsheet
  - [Setup Instructions](GoogleSheetsIntegration.md)

## Troubleshooting 🔍

### Common Issues

1. **Bot not responding**
   - Verify your tokens in `.env`
   - Make sure Socket Mode is enabled
   - Check app permissions

2. **Cannot post in channel**
   - Invite the bot to the channel first
   - Verify bot has correct permissions

3. **"not_allowed_token_type" error**
   - Make sure your app token starts with `xapp-`
   - Verify it has the `connections:write` scope

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- [Slack Bolt Framework](https://slack.dev/bolt-python/tutorial/getting-started)
- [Socket Mode documentation](https://api.slack.com/apis/connections/socket) 
