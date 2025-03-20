import telebot
import os

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Validate environment variables
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

# Load environment variables
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TELEGRAM_CHAT_ID:
    chat_ids = [int(TELEGRAM_CHAT_ID)]
else:
    chat_ids = []

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['chatid'])
def send_chatid(message: telebot.types.Message) -> None:
    bot.reply_to(message, f"Your chat id is {message.chat.id}")


@bot.message_handler(commands=['start'])
def handle_start(message: telebot.types.Message):
    if not message.chat.id in chat_ids:
        chat_ids.append(message.chat.id)
    bot.reply_to(message, f"This bot will notify you if some IoT device registered {message.chat.id}")

def send_telegram_notification(message: str):
    """Send a notification message to the configured Telegram chat."""
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id, message)
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")

def start_bot():
    """Runs the Telegram bot polling"""
    bot.polling(none_stop=True)

if __name__ == "__main__":
    send_telegram_notification("Hello there?")
    bot.infinity_polling()
    # never go here


