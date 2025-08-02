import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
import time
from datetime import datetime
import requests
import json
from requests.auth import HTTPBasicAuth
from config import RECOGNITION_TYPES, DEFAULT_EMOJI, SHEETS_CONFIG
from sheets_integration import sheets

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

#---------------------------
# Helper Functions
#---------------------------

def extract_user_mention(rich_text_input):
    """
    Extract user mentions from a rich text input.
    Returns a dict with:
    - mention_count: number of users mentioned
    - user_id: ID of the first mentioned user (if any)
    - mentioned_users: list of all mentioned user IDs
    """
    result = {
        "mention_count": 0,
        "user_id": None,
        "mentioned_users": []
    }
    
    if not rich_text_input or "rich_text_value" not in rich_text_input:
        return result
        
    rich_text = rich_text_input["rich_text_value"]
    
    if "elements" in rich_text:
        for block in rich_text["elements"]:
            if block["type"] == "rich_text_section":
                for element in block["elements"]:
                    if element["type"] == "user":
                        result["mention_count"] += 1
                        # Store the user ID
                        result["mentioned_users"].append(element["user_id"])
                        # Store the first user ID we find
                        if result["user_id"] is None:
                            result["user_id"] = element["user_id"]
    
    return result

def extract_rich_text_content(rich_text_input):
    """Extract content from rich text input, handling all rich text elements."""
    if not rich_text_input or "rich_text_value" not in rich_text_input:
        return ""
        
    message_content = ""
    rich_text = rich_text_input["rich_text_value"]
    
    if "elements" in rich_text:
        for block in rich_text["elements"]:
            if block["type"] == "rich_text_section":
                message_content += process_rich_text_section(block)
            elif block["type"] == "rich_text_list":
                message_content += process_rich_text_list(block)
            elif block["type"] == "rich_text_preformatted":
                message_content += process_rich_text_preformatted(block)
            elif block["type"] == "rich_text_quote":
                message_content += process_rich_text_quote(block)
    
    return message_content.strip()

def process_rich_text_section(section):
    """Process a rich text section element."""
    content = ""
    
    if "elements" in section:
        for element in section["elements"]:
            if element["type"] == "text":
                text = element["text"]
                
                # Apply text styling if present
                style = element.get("style", {})
                if style.get("bold"):
                    text = f"*{text}*"
                if style.get("italic"):
                    text = f"_{text}_"
                if style.get("strike"):
                    text = f"~{text}~"
                if style.get("code"):
                    text = f"`{text}`"
                    
                content += text
                
            elif element["type"] == "emoji":
                content += f":{element['name']}:"
                
            elif element["type"] == "user":
                content += f"<@{element['user_id']}>"
                
            elif element["type"] == "channel":
                content += f"<#{element['channel_id']}>"
                
            elif element["type"] == "usergroup":
                content += f"<!subteam^{element['usergroup_id']}>"
                
            elif element["type"] == "link":
                url = element["url"]
                text = element.get("text", url)
                if text != url:
                    content += f"<{url}|{text}>"
                else:
                    content += url
                    
            elif element["type"] == "broadcast":
                range_type = element.get("range", "here")
                content += f"<!{range_type}>"
                
    return content

def process_rich_text_list(list_block):
    """Process a rich text list element."""
    content = "\n"
    style = list_block.get("style", "bullet")
    indent = list_block.get("indent", 0)
    
    if "elements" in list_block:
        for i, item in enumerate(list_block["elements"]):
            if item["type"] == "rich_text_section":
                # Add proper indentation
                indent_str = "  " * indent
                
                # Add bullet or number
                if style == "bullet":
                    bullet = "• "
                else:  # ordered list
                    bullet = f"{i + 1}. "
                
                item_content = process_rich_text_section(item)
                content += f"{indent_str}{bullet}{item_content}\n"
                
    return content

def process_rich_text_preformatted(preformatted):
    """Process a rich text preformatted (code block) element."""
    content = "\n```"
    
    if "elements" in preformatted:
        for element in preformatted["elements"]:
            if element["type"] == "text":
                content += element["text"]
                
    content += "```\n"
    return content

def process_rich_text_quote(quote):
    """Process a rich text quote element."""
    content = "\n> "
    
    if "elements" in quote:
        for element in quote["elements"]:
            if element["type"] == "text":
                # Replace newlines with quoted newlines
                text = element["text"].replace("\n", "\n> ")
                content += text
                
    content += "\n"
    return content

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
    ###remove the hardcoding and tag your leadership slack handle as a CC.
    ###f"*CC:* <!subteam^tech-manager|@tech-manager>"
    return (
        f"{DEFAULT_EMOJI} *Thanks <@{recipient_id}> for being a "
        f"{recognition['title']} {recognition['emoji']} * {DEFAULT_EMOJI}\n\n"
        f"*Message:*\n{message_content}\n\n"
        f"*From:* <@{sender_id}>\n"
    )

#---------------------------
# Event Handlers
#---------------------------

@app.event("message")
def handle_message_events(body, logger):
    """Handle incoming message events."""
    logger.info("Received message event")
    return

#---------------------------
# Command Handlers
#---------------------------

@app.command("/kudos") 
def handle_kudos_command(ack, body, client, logger):
    """Handle the /kudos slash command by opening the kudos modal."""
    # Acknowledge immediately to prevent trigger_id expiration
    ack()
    
    try:
        # Get the user who triggered the command
        user_id = body["user_id"]
        
        # Get user information including email
        try:
            user_info = client.users_info(user=user_id)
            user_email = user_info["user"].get("profile", {}).get("email")
            user_name = user_info["user"].get("real_name")
            logger.info(f"Command triggered by {user_name} ({user_email})")
        except Exception as email_error:
            logger.error(f"Error fetching user email: {email_error}")
            user_email = None
        
        # Get channel ID
        channel_id = body.get("channel_id")
        if not channel_id:
            client.chat_postMessage(
                channel=user_id,
                text="Please use this command in a channel to give kudos."
            )
            return

        # Create options before opening modal
        recognition_options = create_recognition_options()
        
        # Open the modal with rich text input for user mentions
        logger.info("Received kudos command - opening modal with rich text input")
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "kudos_modal",
                "private_metadata": channel_id,
                "title": {
                    "type": "plain_text",
                    "text": f"🎉 Give Kudos"
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
                            "text": "👥 Mention Coworker (One Person Only)"
                        },
                        "element": {
                            "type": "rich_text_input",
                            "action_id": "recipient_mention",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "@mention exactly one coworker"
                            }
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
                                "text": "Write your kudos message here... You can use @mentions, emojis, bullet points, formatting, and links!"
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

#---------------------------
# View Submission Handlers
#---------------------------

@app.view("kudos_modal")
def handle_kudos_submission(ack, body, client, view, logger):
    """Handle the submission of the kudos modal."""
    try:
        # First validate that exactly one user is mentioned
        recipient_mention = view["state"]["values"]["recipient_block"]["recipient_mention"]
        recipient_data = extract_user_mention(recipient_mention)
        
        # Log what we found for debugging
        logger.info(f"Mentions found: {recipient_data['mention_count']}")
        if recipient_data["mentioned_users"]:
            logger.info(f"Mentioned users: {recipient_data['mentioned_users']}")
        
        # Check if we have exactly one user mention
        if recipient_data["mention_count"] == 0:
            # Respond with error if no user mentioned
            ack({
                "response_action": "errors",
                "errors": {
                    "recipient_block": "Please @mention a coworker to give kudos to."
                }
            })
            return
        elif recipient_data["mention_count"] > 1:
            # Respond with error if multiple users mentioned
            ack({
                "response_action": "errors",
                "errors": {
                    "recipient_block": f"You mentioned {recipient_data['mention_count']} people. Please mention ONLY ONE coworker."
                }
            })
            return
        
        # We have exactly one mention, proceed
        recipient_id = recipient_data["user_id"]
        
        if not recipient_id:
            # Respond with error if we couldn't extract the user ID
            ack({
                "response_action": "errors",
                "errors": {
                    "recipient_block": "Couldn't recognize the mentioned user. Please try again."
                }
            })
            return
        
        # Extract other submission values
        recognition_type = view["state"]["values"]["recognition_type_block"]["recognition_type_select"]["selected_option"]["value"]
        message_input = view["state"]["values"]["message_block"]["message_input"]
        
        # Acknowledge the submission
        ack()
        logger.info("Kudos submission received - processing now")
        
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
                # Send the message to the channel
                client.chat_postMessage(
                    channel=channel_id,
                    text=kudos_message
                )
                
                # Try to log the recognition to Google Sheets
                log_recognition_to_sheets(
                    client=client, 
                    body=body,
                    recipient_id=recipient_id, 
                    recognition_type=recognition_type, 
                    recognition=recognition,
                    message_content=message_content, 
                    channel_id=channel_id,
                    logger=logger
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

#---------------------------
# Google Sheets Integration
#---------------------------

def log_recognition_to_sheets(client, body, recipient_id, recognition_type, recognition, message_content, channel_id, logger):
    """Log recognition to Google Sheets."""
    logger.info("===== STARTING GOOGLE SHEETS LOGGING =====")
    
    # Check sheets integration state before proceeding
    logger.info(f"Sheets integration initialized: {sheets.initialized}")
    logger.info(f"Sheets integration spreadsheet_id: {sheets.spreadsheet_id}")
    logger.info(f"Sheets integration credentials_path: {sheets.credentials_path}")
    logger.info(f"Credentials file exists: {os.path.exists(sheets.credentials_path)}")
    
    try:
        # Get user information for better logging
        logger.info(f"Getting user info for sender: {body['user']['id']}")
        sender_info = client.users_info(user=body["user"]["id"])
        sender_email = sender_info["user"].get("profile", {}).get("email", "")
        logger.info(f"Getting user info for recipient: {recipient_id}")
        recipient_info = client.users_info(user=recipient_id)
        recipient_email = recipient_info["user"].get("profile", {}).get("email", "")
        
        # Log the recognition to Google Sheets
        recognition_data = {
            'recipient_name': recipient_info["user"]["real_name"],
            'recipient_id': recipient_id,
            'recipient_email': recipient_email,
            'recognition_type': f"{recognition['title']} ({recognition_type})",
            'message': message_content,
            'sender_name': sender_info["user"]["real_name"],
            'sender_id': body["user"]["id"],
            'sender_email': sender_email,
            'channel_id': channel_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add detailed logging for debugging Google Sheets integration
        logger.info(f"Attempting to log recognition to Google Sheets: {recognition_data}")
        
        # Try creating a fresh sheets instance to see if that helps
        logger.info("Creating a fresh sheets instance for this logging attempt")
        import sheets_integration
        from sheets_integration import SheetsIntegration
        fresh_sheets = SheetsIntegration()
        
        if fresh_sheets.initialized:
            logger.info("Fresh sheets instance initialized successfully")
            # Use the fresh instance to log
            sheets_result = fresh_sheets.log_recognition(recognition_data)
            logger.info(f"Fresh sheets logging result: {sheets_result}")
        else:
            logger.warning("Fresh sheets instance failed to initialize")
            # Try with the original instance as fallback
            sheets_result = sheets.log_recognition(recognition_data)
            logger.info(f"Original sheets logging result: {sheets_result}")
        
        logger.info("===== COMPLETED GOOGLE SHEETS LOGGING =====")
        return sheets_result
    except Exception as sheets_error:
        logger.error(f"Error during sheets logging process: {sheets_error}")
        logger.exception("Full exception details:")
        return False

# Add this function to trigger Airflow DAG
def trigger_airflow_dag(dag_id, conf=None, logger=None):
    """
    Trigger an Airflow DAG run using the REST API
    
    Args:
        dag_id (str): The ID of the DAG to trigger
        conf (dict, optional): Configuration/parameters to pass to the DAG
        logger (Logger, optional): Logger instance
    
    Returns:
        dict: The response from the Airflow API
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    if conf is None:
        conf = {}
    
    try:
        logger.info(f"Attempting to trigger Airflow DAG: {dag_id}")
        
        # Create the URL for triggering a DAG run
        url = f"{AIRFLOW_CONFIG['api_base_url']}/dags/{dag_id}/dagRuns"
        
        # Prepare the authentication
        auth = HTTPBasicAuth(AIRFLOW_CONFIG['username'], AIRFLOW_CONFIG['password'])
        
        # Prepare the request payload
        payload = {
            "conf": conf,
        }
        
        # Make the API request
        response = requests.post(
            url,
            auth=auth,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Get the JSON response
        result = response.json()
        logger.info(f"Successfully triggered DAG {dag_id}, run ID: {result.get('dag_run_id', 'unknown')}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error triggering Airflow DAG {dag_id}: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response status: {e.response.status_code}, Response body: {e.response.text}")
        return {"error": str(e)}

# Add a new command to trigger an Airflow DAG
@app.command("/trigger-dag")
def handle_trigger_dag_command(ack, body, client, logger):
    """Handle the /trigger-dag slash command to run an Airflow DAG."""
    # Acknowledge immediately to prevent trigger_id expiration
    ack()
    
    try:
        # Get the user who triggered the command
        user_id = body["user_id"]
        
        # Get user information including email
        try:
            user_info = client.users_info(user=user_id)
            user_email = user_info["user"].get("profile", {}).get("email")
            user_name = user_info["user"]["real_name"]
            logger.info(f"DAG trigger command by {user_name} ({user_email})")
        except Exception as email_error:
            logger.error(f"Error fetching user email: {email_error}")
            user_email = None
        
        # Get the text from the command which should contain the DAG ID
        command_text = body.get("text", "").strip()
        
        if not command_text:
            # Show an error if no DAG ID was provided
            client.chat_postMessage(
                channel=user_id,
                text="Please provide a DAG ID. Usage: /trigger-dag <dag_id> [optional JSON parameters]"
            )
            return
        
        # Split the command text to get the DAG ID and optional JSON parameters
        parts = command_text.split(" ", 1)
        dag_id = parts[0]
        
        # Parse any additional parameters if provided
        conf = {}
        if len(parts) > 1:
            try:
                conf = json.loads(parts[1])
                logger.info(f"Parsed parameters for DAG: {conf}")
            except json.JSONDecodeError:
                client.chat_postMessage(
                    channel=user_id,
                    text=f"Invalid JSON parameters. Make sure your parameters are valid JSON."
                )
                return
        
        # Add the user information to the configuration
        conf["triggered_by_user"] = {
            "id": user_id,
            "name": user_name,
            "email": user_email
        }
        
        # Trigger the DAG
        result = trigger_airflow_dag(dag_id, conf, logger)
        
        if "error" in result:
            # There was an error triggering the DAG
            client.chat_postMessage(
                channel=user_id,
                text=f"Error triggering DAG {dag_id}: {result['error']}"
            )
        else:
            # DAG was triggered successfully
            client.chat_postMessage(
                channel=user_id,
                text=f"Successfully triggered DAG {dag_id}.\nRun ID: {result.get('dag_run_id', 'unknown')}"
            )
            
            # Also send a message to the channel where the command was triggered
            channel_id = body.get("channel_id")
            if channel_id:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"DAG {dag_id} was triggered by <@{user_id}>.\nRun ID: {result.get('dag_run_id', 'unknown')}"
                )
        
    except Exception as e:
        logger.error(f"Error handling trigger-dag command: {e}")
        logger.exception("Full error details:")
        client.chat_postMessage(
            channel=body["user_id"],
            text=f"Sorry, there was an error triggering the DAG: {str(e)}"
        )

#---------------------------
# Main Application Startup
#---------------------------

if __name__ == "__main__":
    try:
        logger.info("Starting the app in Socket Mode...")
        
        # Verify Google Sheets integration
        if SHEETS_CONFIG.get("enabled", True):
            sheet_id = os.environ.get("GOOGLE_SHEET_ID")
            creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", 
                                       SHEETS_CONFIG.get("default_credentials_path", "credentials.json"))
            
            if sheet_id and os.path.exists(creds_path):
                logger.info(f"Google Sheets integration enabled with sheet ID: {sheet_id}")
                logger.info(f"Using credentials from: {creds_path}")
                
                # Force reinitialization of sheets integration
                import sheets_integration
                from sheets_integration import SheetsIntegration
                sheets_integration.sheets = SheetsIntegration()
                
                if sheets_integration.sheets.initialized:
                    logger.info("Google Sheets integration initialized successfully")
                else:
                    logger.warning("Google Sheets integration failed to initialize")
            else:
                if not sheet_id:
                    logger.warning("GOOGLE_SHEET_ID not set in environment variables")
                if not os.path.exists(creds_path):
                    logger.warning(f"Credentials file not found at {creds_path}")
        
        # Start Socket Mode handler
        handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
        handler.start()
    except Exception as e:
        logger.error("Error starting the app: %s", str(e))
        raise