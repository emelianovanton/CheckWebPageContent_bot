import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Job, MessageHandler, Filters

url_to_check = os.environ.get('WEBPAGE_URL')
bot_token = os.environ.get('BOT_TOKEN')
channel_id = os.environ.get('CHANNEL_ID')
update_frequency = int(os.environ.get('UPDATE_FREQ_SEC'))
previous_content = ''


def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id,
                             'Bot is running. Use /runcheck to manually check.')


def check(context: CallbackContext) -> None:
    global previous_content
    try:
        response = requests.get(url_to_check)
        soup = BeautifulSoup(response.text, 'html.parser')
        current_content = str(soup)

        if current_content != previous_content:
            context.bot.send_message(channel_id, f'\U0001F6A8\U0001F6A8\U0001F6A8  \n'
                                                 f'Web page content changed!\n '
                                                 f'{url_to_check}')
            previous_content = current_content

    except Exception as e:
        context.bot.send_message(channel_id, f'Error: {str(e)}')
    context.bot.send_message(channel_id, f'Check completed.')


def manual_check(context: CallbackContext) -> None:
    context.bot.send_message(channel_id, f'Checking...')
    check()
    context.bot.send_message(channel_id, f'Check completed.')


def run_manual_check(update: Update, context: CallbackContext) -> None:
    manual_check(context)


def run_check(update: Update, context: CallbackContext) -> None:
    check(context)


def main() -> None:
    updater = Updater(bot_token)
    job_queue = updater.job_queue

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("runcheck", run_check))

    # Schedule the check job every 5 minutes
    job_queue.run_repeating(check, interval=update_frequency, first=30)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
