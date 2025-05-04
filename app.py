import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify
from slack_sdk.errors import SlackApiError
import time
from datetime import datetime
from config import RECOGNITION_TYPES, DEFAULT_EMOJI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask app
flask_app = Flask(__name__)

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Create SlackRequestHandler
handler = SlackRequestHandler(app)

def extract_rich_text_content(rich_text_input):
    """Extract content from rich text input, handling text and emojis."""
    if not rich_text_input or "rich_text_value" not in rich_text_input:
        return ""
        
    message_content = ""
    rich_text = rich_text_input["rich_text_value"]
    
    if "elements" in rich_text:
        for block in rich_text["elements"]:
            if block["type"] == "rich_text_section":
                for element in block["elements"]:
                    if element["type"] == "text":
                        message_content += element["text"]
                    elif element["type"] == "emoji":
                        message_content += f":{element['name']}:"
    
    return message_content

def create_user_options(users):
    """Create user options for the dropdown menu."""
    return [
        {
            "text": {
                "type": "plain_text",
                "text": user["real_name"]
            },
            "value": user["id"]
        }
        for user in users if not user["is_bot"] and not user["deleted"]
    ]

def create_recognition_options():
    """Create recognition type options for the dropdown menu."""
    return [
        {
            "text": {
                "type": "plain_text",
                "text": f"{recognition['emoji']} {recognition['title']}"
            },
            "value": recognition_type
        }
        for recognition_type, recognition in RECOGNITION_TYPES.items()
    ]

def create_kudos_message(recipient_id, recognition, message_content, sender_id):
    """Create the formatted kudos message."""
    return (
        f"{DEFAULT_EMOJI} *Thanks <@{recipient_id}> for being a "
        f"{recognition['title']} {recognition['emoji']} * {DEFAULT_EMOJI}\n\n"
        f"*Message:*\n{message_content}\n\n"
        f"*From:* <@{sender_id}>\n"
    )

# Handle Slack events
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# Handle message events
@app.event("message")
def handle_message_events(body, logger):
    logger.info("Received message event")
    return

# Handle slash command
@app.command("/kudos")
def handle_kudos_command(ack, body, client, logger):
    ack()
    
    try:
        channel_id = body.get("channel_id")
        if not channel_id:
            client.chat_postMessage(
                channel=body["user_id"],
                text="Please use this command in a channel to give kudos."
            )
            return

        # Get users and create options
        users_response = client.users_list()
        user_options = create_user_options(users_response["members"])
        recognition_options = create_recognition_options()

        # Open the modal
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "kudos_modal",
                "private_metadata": channel_id,
                "title": {
                    "type": "plain_text",
                    "text": "🎉 Give Kudos"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Send Kudos"
                },
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "recipient_block",
                        "label": {
                            "type": "plain_text",
                            "text": "👥 Select Coworker"
                        },
                        "element": {
                            "type": "static_select",
                            "action_id": "recipient_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select a coworker"
                            },
                            "options": user_options
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "recognition_type_block",
                        "label": {
                            "type": "plain_text",
                            "text": "🏆 Recognition Type"
                        },
                        "element": {
                            "type": "static_select",
                            "action_id": "recognition_type_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select recognition type"
                            },
                            "options": recognition_options
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "message_block",
                        "label": {
                            "type": "plain_text",
                            "text": "💬 Message"
                        },
                        "element": {
                            "type": "rich_text_input",
                            "action_id": "message_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Write your kudos message here... You can use emojis and @mention people!"
                            }
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error opening modal: {e}")
        client.chat_postMessage(
            channel=body["user_id"],
            text="Sorry, there was an error opening the kudos form. Please try again."
        )

# Handle modal submission
@app.view("kudos_modal")
def handle_kudos_submission(ack, body, client, view):
    ack()
    
    try:
        # Extract values from the submission
        recipient_id = view["state"]["values"]["recipient_block"]["recipient_select"]["selected_option"]["value"]
        recognition_type = view["state"]["values"]["recognition_type_block"]["recognition_type_select"]["selected_option"]["value"]
        message_input = view["state"]["values"]["message_block"]["message_input"]
        
        # Process the message content
        message_content = extract_rich_text_content(message_input)
        logger.info(f"Extracted message content: {message_content}")
        
        # Get recognition details
        recognition = RECOGNITION_TYPES.get(recognition_type, {"title": "Team Member", "emoji": "👏"})
        
        # Create and send the kudos message
        kudos_message = create_kudos_message(
            recipient_id,
            recognition,
            message_content,
            body["user"]["id"]
        )
        
        # Post the message to the channel
        channel_id = view["private_metadata"]
        if channel_id:
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    text=kudos_message
                )
            except SlackApiError as e:
                if e.response["error"] == "not_in_channel":
                    client.chat_postMessage(
                        channel=body["user"]["id"],
                        text=f"I need to be invited to the channel first. Please invite me to <#{channel_id}> and try again."
                    )
                else:
                    raise
        else:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text="Please use the command in a channel to give kudos."
            )
        
    except Exception as e:
        logger.error(f"Error handling kudos submission: {e}")
        logger.error(f"Full error details: {str(e)}")
        client.chat_postMessage(
            channel=body["user"]["id"],
            text="Sorry, there was an error submitting your kudos. Please try again."
        )

# Start your app
if __name__ == "__main__":
    try:
        logger.info("Starting the app...")
        flask_app.run(port=3000)
    except Exception as e:
        logger.error("Error starting the app: %s", str(e))
        raise