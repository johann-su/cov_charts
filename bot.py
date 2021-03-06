from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, PicklePersistence,  MessageHandler, Filters, CallbackQueryHandler
from charts import Chart

# sends an image of a chart with user specified parameters
def chart(update: Update, context: CallbackContext) -> None:
    reply_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("line", callback_data='line'),
            InlineKeyboardButton("bar", callback_data='bar'),
            InlineKeyboardButton("geo", callback_data='geo')
        ],
    ])
    update.message.reply_text(
        f'Hello {update.effective_user.first_name}, please choose an option:',
        reply_markup=reply_buttons
    )

# updates the question to the user and sends image
def button(update: Update, context: CallbackContext) -> None:
    # Must call answer!
    update.callback_query.answer()
    # Remove buttons
    update.callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([])
    )
    # send image
    chart=Chart(data = 'cases', timeframe = '1W', chart = update.callback_query.data, state = 'Sachsen')
    path = chart.plot()

    bot.send_photo(chat_id, open(path,'rb'))
    # update.callback_query.message.reply_dice(emoji=update.callback_query.data)

# lets the user set default chart options
def setup(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')
    
bot = Bot()
updater = Updater(bot=bot)

try:
    chat_id = bot.get_updates()[-1].message.chat_id
except IndexError:
    chat_id = 0

updater.dispatcher.add_handler(CommandHandler('chart', chart))
updater.dispatcher.add_handler(CommandHandler('setup', setup))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()