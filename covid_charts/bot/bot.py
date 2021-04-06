import logging
from typing import Dict, List, Callable, Optional
from telegram.utils.request import Request

from telegram import Update, Bot
from telegram.ext import  Updater, CallbackContext, PicklePersistence

LOGGER = logging.getLogger(__name__)

def log_error(update: Update, context):
    LOGGER.fatal(context.error, exc_info=True)

def run(token: str, handlers: List[Callable]):
    bot = Bot(token, request=Request(
        con_pool_size=10, connect_timeout=40))
    updater = Updater(bot=bot, use_context=True, persistence=PicklePersistence(filename='bot_data'))

    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.dispatcher.add_error_handler(log_error)
    updater.start_polling()
    updater.idle()
