import logging
import os
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import requests

from dotenv import load_dotenv
from llm.models import interact_with_ai

# Load environment variables from .env file
load_dotenv()

# Configure basic logging
logging.basicConfig(
    format='%(levelname)s: %(name)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def to_bool(env):
  return os.getenv(env, 'False').lower() in ('true', '1', 't')

def escape_telegram_markdown(text):
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`");

app = FastAPI()
# Get bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
UVICORN_PORT = os.getenv("UVICORN_PORT")
ALLOWED_CHAT_IDS = [int(id) for id in os.getenv("ALLOWED_CHAT_IDS").split(",")]

AI_CONFIG = {
  "system_prompt": os.getenv("AI_SYS_PROMPT"),
  "protocol": os.getenv("AI_PROTO"),
  "hostname": os.getenv("AI_HOST"),
  "port": os.getenv("AI_PORT"),
  "model": os.getenv("AI_MODEL"),
  "temperature": float(os.getenv("AI_TEMP")),
  "num_ctx": int(os.getenv("AI_CTX")),
  "stream": to_bool(os.getenv("AI_STREAM")),
  "show_stats": to_bool(os.getenv("AI_STATS")),
  "context_keep": int(os.getenv("AI_CONTEXT_KEEP")),
  "context_max": int(os.getenv("AI_CONTEXT_MAX")),
  "max_iter": int(os.getenv("AI_MAX_TOOL_ITER"))
}

def process_message(message: dict):
    """Message processing with logging"""
    logger.info("Starting message processing")
    try:
        logger.debug(f"Raw message data: {message}")

        if "message" in message:
            user_request = message["message"].get("text")
            chat_id = message["message"]["chat"].get("id")

            if user_request=="/start":
                send_telegram_reply(chat_id, f"Welcome!")
            elif user_request=="/wipe":
                os.remove(f"data/{chat_id}.json")
            else:
                if user_request and chat_id and chat_id in ALLOWED_CHAT_IDS:
                    logger.info(f"Message from {chat_id}: {user_request}")
                    llm_response = interact_with_ai(user_request, chat_id, AI_CONFIG)
                    send_telegram_reply(chat_id, f"{llm_response}")
                else:
                    logger.warning(f"Received message from {chat_id}: {text} [NOT ALLOWED USER]")
                    send_telegram_reply(chat_id, f"You're NOT allowed to use this bot")

    except Exception as e:
        logger.error(f"Error processing message: {e}")

def send_telegram_reply(chat_id: int, text: str):
    """Send message with error handling and logging"""
    try:
        escaped_text = escape_telegram_markdown(text)

        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": escaped_text, "parse_mode": "Markdown"},
            timeout=5
        )
        #logger.info(response.__dict__)
        response.raise_for_status()
        logger.info(f"Message sent to {chat_id}")

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        logger.error(f"Content: {text}")

@app.post("/aibot")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook endpoint with access logging"""
    client_ip = request.client.host
    logger.info(f"Incoming request from IP: {client_ip}")

    data = await request.json()
    background_tasks.add_task(process_message, data)

    return {"status": "received"}

@app.get("/status")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Webhook healthcheck with access logging"""
    client_ip = request.client.host
    logger.info(f"Incoming request from IP: {client_ip}")

    return {"status": "ok"}

if __name__ == "__main__":
    print(f"Allowed chat IDS: {ALLOWED_CHAT_IDS}")
    uvicorn.run(app, host="0.0.0.0", port=int(UVICORN_PORT))
