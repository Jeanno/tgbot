from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import info_db
import config

info_list = None
reply_markup = None

def setup_info():
    global info_list, reply_markup

    info_list = info_db.fetch()

    keyboard = []
    current_ary = []
    count = 0
    for info in info_list:
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

    reply_markup = InlineKeyboardMarkup(keyboard)


def info(bot, update):
    setup_info()
    update.message.reply_text('請選擇：', reply_markup=reply_markup)


def button(bot, update):
    setup_info()
    query = update.callback_query

    message = "發生錯誤，請再試。"
    for info in info_list:
        if query.data == info[0]:
            message = info[1]
            break

    query.edit_message_text(text=message + " ", reply_markup=reply_markup)


def error(bot, update, e):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, e)


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
    setup_info()
    main()

