import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Job, MessageHandler, Filters

url_to_check = os.environ.get('WEBPAGE_URL')
bot_token = os.environ.get('BOT_TOKEN')
channel_id = os.environ.get('CHANNEL_ID')
previous_content = ''
user_ids = set()


def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id,
                             'Bot is running. Use /check to get the web page content or /runcheck to manually check.')


def check(context: CallbackContext) -> None:
    global previous_content

    try:
        response = requests.get(url_to_check)
        soup = BeautifulSoup(response.text, 'html.parser')
        current_content = str(soup)

        if current_content != previous_content:
            context.bot.send_message(channel_id, 'Web page content changed!\n\n' + current_content)
            previous_content = current_content
        else:
            context.bot.send_message(channel_id, 'Web page content remains the same.')

    except Exception as e:
        context.bot.send_message(channel_id, f'Error: {str(e)}')


def run_check(update: Update, context: CallbackContext) -> None:
    check(context)


def main() -> None:
    updater = Updater(bot_token)
    job_queue = updater.job_queue

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("runcheck", run_check))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, run_check))

    # Schedule the check job every 5 minutes
    job_queue.run_repeating(check, interval=300, first=0)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
