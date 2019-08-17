from datetime import datetime, timedelta
import threading
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import google.cloud.logging
import logging

import info_db
import config

info_lock = threading.Lock()
info_list = None
reply_markup = None
last_update = None

client = google.cloud.logging.Client()
client.setup_logging()

def load_info():
    info_lock.acquire()
    global info_list, reply_markup, last_update

    if last_update and datetime.now() < last_update + timedelta(minutes=1):
        info_lock.release()
        return

    try:
        info_list_local = info_db.fetch()
        keyboard = []
        current_ary = []
        count = 0
        for info in info_list_local:
            if count == 0:
                count += 1
                continue
            current_ary.append(InlineKeyboardButton(info[0], callback_data=info[0]))
            if len(current_ary) == 2:
                keyboard.append(current_ary)
                current_ary = []
            count += 1
        if len(current_ary) > 0:
            keyboard.append(current_ary)

        info_list = info_list_local
        reply_markup = InlineKeyboardMarkup(keyboard)
        last_update = datetime.now()
        logging.info("{} - Finished updating info".format(str(datetime.now())))
    except:
        print('Error occur while updating info.')
    finally:
        info_lock.release()



def info(bot, update):
    load_info()
    update.message.reply_text('請選擇：', reply_markup=reply_markup)


def button(bot, update):
    load_info()
    query = update.callback_query

    message = "發生錯誤，請再試。"
    for info in info_list:
        if query.data == info[0]:
            message = info[1]
            break

    logging.info("{} - Query {}".format(str(datetime.now()), info[0]))
    query.edit_message_text(text=message + " ", reply_markup=reply_markup)


def error(bot, update, e):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, e)


def main():
    updater = Updater(config.TG_TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', info))
    updater.dispatcher.add_handler(CommandHandler('info', info))
    updater.dispatcher.add_handler(CommandHandler('help', info))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

