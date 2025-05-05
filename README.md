# Kudos Slack Bot 🎉

A Slack bot that allows team members to give kudos to their colleagues with customizable recognition types and emojis.

## Features ✨

- Customizable recognition types and emojis
- Rich text message support with emoji support
- User-friendly modal interface
- Channel-based kudos sharing
- Easy configuration through `config.py`
- Global shortcut for quick access
- Socket Mode support (no need for ngrok)

## Prerequisites 📋

- Python 3.7 or higher
- A Slack workspace
- Slack app with appropriate permissions

## Setup Instructions 🛠️

### 1. Local Development Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/jinagamvasubabu/kudos-slack-bot.git
   cd kudos-slack-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_SIGNING_SECRET=your-signing-secret
   SLACK_APP_TOKEN=xapp-your-app-token
   ```

5. Run the application:
   ```bash
   python app.py
   ```

### 2. Create a Slack App (Ensure you have necessary permissions to do this, else take help from your administrator in setting up this)

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Enter your app name and select your workspace
5. Under "Add features and functionality", click on "Bots"
6. Click "Review Scopes to Add"

### 3. Configure Slack App Permissions

Add the following OAuth scopes to your bot:
- `chat:write` - To send messages
- `commands` - To add slash commands
- `users:read` - To get user information
- `users:read.email` - To read user email addresses
- `commands` - To add slash commands
- `shortcuts` - To add global shortcuts

### 4. Enable Socket Mode

1. Go to "Socket Mode" in your app settings
2. Toggle "Enable Socket Mode" to On
3. Generate an App-Level Token with the `connections:write` scope
4. Copy the generated token to your `.env` file as `SLACK_APP_TOKEN`

### 5. Install the App to Your Workspace

1. Go to "OAuth & Permissions" in your app settings
2. Click "Install to Workspace"
3. Authorize the app

### 6. Set Up Slash Command

1. Go to "Slash Commands" in your app settings
2. Click "Create New Command"
3. Fill in the following:
   - Command: `/kudos`
   - Short Description: "Give kudos to a team member"
   - Usage Hint: `[@user] [message]`

### 7. Set Up Global Shortcut

1. Go to "Interactivity & Shortcuts" in your app settings
2. Enable Interactivity
3. Under "Global Shortcuts", click "Create New Shortcut"
4. Fill in the following:
   - Name: "Give Kudos"
   - Description: "Quickly give kudos to a team member"
   - Callback ID: `kudos_shortcut`

## Configuration 🛠️

You can customize the recognition types and emojis by editing `config.py`:

```python
RECOGNITION_TYPES = {
    "silent_soldier": {
        "title": "Silent Soldier",
        "emoji": "🥷"
    },
    # Add more recognition types here
}
```

## Usage 📝

### Using Slash Command
1. In any Slack channel, type `/kudos`
2. Select a team member from the dropdown
3. Choose a recognition type
4. Write your kudos message (supports emojis and @mentions)
5. Click "Send Kudos"

### Using Global Shortcut
1. Click the "+" button next to the message input
2. Select "Give Kudos" from the shortcuts menu
3. Select a team member from the dropdown
4. Choose a recognition type
5. Write your kudos message
6. Click "Send Kudos"

## Troubleshooting 🔍

### Common Issues

1. **Bot not responding**
   - Check if the bot is installed in the workspace
   - Verify the bot token in `.env`
   - Ensure Socket Mode is enabled

2. **Cannot post in channel**
   - Make sure the bot is invited to the channel
   - Check if the bot has the required permissions

3. **Emojis not displaying correctly**
   - Verify the emoji codes in `config.py`
   - Check if the emoji is supported in Slack

4. **Shortcut not appearing**
   - Verify that the shortcut is properly configured in Slack app settings
   - Check if the bot has the required permissions
   - Try reinstalling the app to the workspace

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- [Slack Bolt Framework](https://slack.dev/bolt-python/tutorial/getting-started)
- [python-dotenv](https://pypi.org/project/python-dotenv/) 
