import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

url_to_check = os.environ.get('WEBPAGE_URL')
bot_token = os.environ.get('BOT_TOKEN')
previous_content = ''
user_ids = set()


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    user_ids.add(user_id)
    update.message.reply_text('Bot is running. Use /check to get the web page content or /runcheck to manually check.')


def check(context: CallbackContext) -> None:
    global previous_content

    try:
        response = requests.get(url_to_check)
        soup = BeautifulSoup(response.text, 'html.parser')
        current_content = str(soup)

        if current_content != previous_content:
            for user_id in user_ids:
                context.bot.send_message(user_id, 'Web page content changed!\n\n' + current_content)
            previous_content = current_content
        else:
            for user_id in user_ids:
                context.bot.send_message(user_id, 'Web page content remains the same.')

    except Exception as e:
        for user_id in user_ids:
            context.bot.send_message(user_id, f'Error: {str(e)}')


def run_check(update: Update, context: CallbackContext) -> None:
    check(context)


def main() -> None:
    updater = Updater(bot_token)
    job_queue = updater.job_queue

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("runcheck", run_check))

    # Schedule the check job every 2 minutes
    job_queue.run_repeating(check, interval=120, first=0)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
