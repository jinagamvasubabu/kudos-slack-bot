"""
Configuration file for the Kudos Slack bot.
Users can customize recognition types and their corresponding emojis here.
"""

# Recognition types configuration
RECOGNITION_TYPES = {
    "silent_soldier": {
        "title": "Silent Soldier",
        "emoji": "🥷"
    },
    "helping_hand": {
        "title": "Helping Hand",
        "emoji": "🤝"
    },
    "innovation_guru": {
        "title": "Innovation Guru",
        "emoji": "💡"
    },
    "fast_learner": {
        "title": "Fast Learner",
        "emoji": "🚀"
    },
    "problem_solver": {
        "title": "Problem Solver",
        "emoji": "🎯"
    },
    "team_player": {
        "title": "Team Player",
        "emoji": "🤝"
    }
}

# Default emoji for kudos message
DEFAULT_EMOJI = "👏" 

# Google Sheets Configuration
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