import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, PicklePersistence,  MessageHandler, Filters, CallbackQueryHandler
from charts import Chart
from dotenv import load_dotenv
load_dotenv()

# asks the user what chart to show
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
def chart_answer(update: Update, context: CallbackContext) -> None:
    # Must call answer!
    update.callback_query.answer()
    # Remove buttons
    update.callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([])
    )
    # edit query message
    update.callback_query.message.edit_text(
        text=f'Hello {update.effective_user.first_name}, here is your {update.callback_query.data} chart'
    )
    # configure chart
    if context.user_data:
        chart=Chart(
            data = context.user_data['data'], 
            timeframe = context.user_data['tf'], 
            c_type = context.user_data['chart'], 
            state = context.user_data['state'], 
            county = context.user_data['county'],
            comparison = context.user_data['comparison'])
    else:
        chart=Chart(
            data = ['cases'], 
            timeframe = '3W', 
            c_type = update.callback_query.data,
            state = 'Sachsen')

    path = chart.plot()
    bot.send_photo(update.effective_chat.id, open(path,'rb'))

def status(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Cases: {1} + {0}\nDeaths: {2} + {0}\n7 day Incidence: {0.5} + {0.1}')

# lets the user set default chart options
def setup(update: Update, context: CallbackContext) -> None:
    reply_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("line", callback_data='line'),
            InlineKeyboardButton("bar", callback_data='bar'),
            InlineKeyboardButton("geo", callback_data='geo')
        ],
    ])
    update.message.reply_text('Which Chart do you prefer?', reply_markup=reply_buttons)

def receive_info(update: Update, context: CallbackContext) -> None:
    # Must call answer!
    update.callback_query.answer()
    # Remove buttons
    update.callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([])
    )
    context.user_data['chart'] = update.callback_query.data

    
bot = Bot(os.environ['TOKEN'])
updater = Updater(bot=bot, use_context=True, persistence=PicklePersistence(filename='bot_data'))

updater.dispatcher.add_handler(CommandHandler('chart', chart))
updater.dispatcher.add_handler(CallbackQueryHandler(chart_answer))
updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('setup', setup))
updater.dispatcher.add_handler(CallbackQueryHandler(receive_info))

updater.start_polling()
updater.idle()