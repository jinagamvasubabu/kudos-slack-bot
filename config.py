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