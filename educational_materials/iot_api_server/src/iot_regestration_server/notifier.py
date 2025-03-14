import telebot
import logging
import os
import threading

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
#TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_CHAT_ID = None
if TELEGRAM_CHAT_ID:
    chat_ids = [int(TELEGRAM_CHAT_ID)]
else:
    chat_ids = []

# Validate environment variables
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['chatid'])
def send_welcome(message: telebot.types.Message) -> None:
    bot.reply_to(message, f"Your chat id is {message.chat.id}")

@bot.message_handler(commands=['start'])
def send_welcome(message: telebot.types.Message):
    logging.info(f"Got message {message}")
    if not message.chat.id in chat_ids:
        chat_ids.append(message.chat.id)
    bot.reply_to(message, "This bot will notify you if some IoT device registered")

@bot.message_handler(commands=['help'])
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, "No help is provided")

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


