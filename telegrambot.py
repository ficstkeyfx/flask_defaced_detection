API_KEY = "7229699559:AAEPyz5LvrX9IGB-WjXGyNSMJ_5BElpyQaA"
ID = "6651675066"


from telegram import Bot
import asyncio
def send_photo(bot, chat_id, photo_path, caption=None):
    with open(photo_path, 'rb') as photo_file:
        asyncio.run(bot.send_photo(chat_id=chat_id, photo=photo_file, caption=caption))

def send_notification(image, message):
    bot = Bot(token=API_KEY)
    chat_id = ID
    photo_path = image
    caption = message
    send_photo(bot, chat_id, photo_path, caption)

# send_notification("./detection/images/http___www_mustandmore_in_.png", "Detection")