import os
import re
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, PicklePersistence,  MessageHandler, Filters, CallbackQueryHandler
from charts import Chart
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import datetime

# asks the user what chart to show
def chart(update: Update, context: CallbackContext) -> None:
    reply_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("line", callback_data='line')],
        [InlineKeyboardButton("bar", callback_data='bar')],
        [InlineKeyboardButton("geo", callback_data='geo')],
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
        text=f'Hello {update.effective_user.first_name} 👋, here is your {update.callback_query.data} chart'
    )
    # configure chart
    print(context.user_data)
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

# returns the latest information in a simple overview
def status(update: Update, context: CallbackContext) -> None:
    df = pd.read_csv('./data/covid_de.csv')

    tf = df[df['date'] >= df['date'].max()]

    aggregation_functions = {'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    aggregation_functions_state = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    germany =  tf.groupby(tf['date']).aggregate(aggregation_functions)
    state =  tf.groupby(tf['state']).aggregate(aggregation_functions_state)
    
    update.message.reply_text(f"New infections in Germany: {germany['cases'].values[0]}\nNew infections in Saxony: {state.loc[state.index=='Sachsen']['cases'].values[0]}") 

def report(context):
    df = pd.read_csv('./data/covid_de.csv')

    tf = df[df['date'] >= df['date'].max()]

    aggregation_functions = {'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    aggregation_functions_state = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    germany =  tf.groupby(tf['date']).aggregate(aggregation_functions)
    state =  tf.groupby(tf['state']).aggregate(aggregation_functions_state)

    chart=Chart(
            data = ['cases'], 
            timeframe = '3W', 
            c_type = update.callback_query.data,
            state = 'Sachsen')

    path = chart.plot()
    
    context.bot.send_message(chat_id=context.job.context, text=f"New infections in Germany: {germany['cases'].values[0]}\nNew infections in Saxony: {state.loc[state.index=='Sachsen']['cases'].values[0]}")

    context.bot.send_photo(context.job.context, open(path,'rb'))

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                      text='Automatic updates have been enabled.')

    context.job_queue.run_daily(report, time=datetime.time(15, 0, 0), context=update.message.chat_id, name='update')

def stop(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                      text='Automatic updates have been disabled.')
    context.job_queue.stop()

# lets the user set default chart options
def setup(update: Update, context: CallbackContext) -> None:
    reply_list = [f'Hello {update.effective_user.first_name}']
    if context.user_data:
        reply_list.append('Your current config is:')
        reply_list.extend([f'{key}: {value}' for (key, value) in context.user_data.items()])
        
    reply_buttons = ReplyKeyboardMarkup([
        [KeyboardButton("timeframe", callback_data='timeframe'), KeyboardButton("chart type", callback_data='c_type')],
        [KeyboardButton("state", callback_data='state'), KeyboardButton("county", callback_data='county')],
        [KeyboardButton("data", callback_data='data')]
    ], one_time_keyboard=True)
    update.message.reply_text(f'{reply_list}\n\nWhat do you want to configure?', reply_markup=reply_buttons)

TIMEFRAME_REGEX = r'^[0-9]+[DWMY]'
C_TYPE_REGEX = r'(line|bar|geo)'
STATE_REGEX = r'^[A-Za-z]+-?[A-Za-z]+?'
COUNTY_REGEX = r'^[A-Za-z]+\.[LK|SK] [A-Zaz]+-?[A-Za-z]+?'
DATA_REGEX = r'(cases|deaths|incidence) ?ß ?(cases|deaths|incidence)? ?ß ?(cases|deaths|incidence)?'
def receive_info(update: Update, context: CallbackContext) -> None:
    timeframe = re.match(TIMEFRAME_REGEX, update.message.text).group()

    context.user_data['timeframe'] = info

    # Quote the information in the reply
    update.message.reply_text(f'Ok I\'ve set your timeframe to {info}')

def sources(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'My data comes from the RKI and is Updated daily.\nA great overview of this data can be found here: https://npgeo-corona-npgeo-de.hub.arcgis.com\n\nThis is the link to the dataset: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/23b1ccb051f543a5b526021275c1c6e5_0')

def news(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('There are currently no news to show')
    
bot = Bot(os.environ['TOKEN'])
updater = Updater(bot=bot, use_context=True, persistence=PicklePersistence(filename='bot_data'))

updater.dispatcher.add_handler(CommandHandler('start', start, pass_job_queue=True))
updater.dispatcher.add_handler(CommandHandler('start', stop, pass_job_queue=True))
updater.dispatcher.add_handler(CommandHandler('chart', chart))
updater.dispatcher.add_handler(CallbackQueryHandler(chart_answer))
updater.dispatcher.add_handler(CommandHandler('status', status))
updater.dispatcher.add_handler(CommandHandler('setup', setup))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(TIMEFRAME_REGEX), receive_info))
updater.dispatcher.add_handler(CommandHandler('sources', sources))

updater.start_polling()
updater.idle()