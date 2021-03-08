import logging

LOGGER = logging.getLogger(__name__)

def log_error(update: Update, context):
    LOGGER.fatal(context.error, exc_info=True)

def run(token: str, handlers: List[Callable]):
    bot = Bot(token)
    updater = Updater(bot=bot, use_context=True, persistence=PicklePersistence(filename='bot_data'))

    for handler in handlers:
        dp.add_handler(handler)

    updater.dispatcher.add_error_handler(log_error)
    updater.start_polling()
    updater.idle()