import os
import pandas as pd # TODO: Remove when status module is implemented
import random

from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, CallbackContext

from covid_charts.bot.state import States
from covid_charts.bot import setup_conv
from covid_charts.bot import bot
from covid_charts.charts import Chart
from covid_charts.exceptions import DataException

import tweepy

setup_handler = ConversationHandler(
    name='setup_handler',
    entry_points=[CommandHandler('setup', setup_conv.chart_type)],
    states={
        States.CHART_TYPE: [MessageHandler(Filters.text, setup_conv.chart_type)],
        States.TF: [MessageHandler(Filters.text, setup_conv.timeframe)],
        States.REGION: [MessageHandler(Filters.text, setup_conv.region)],
        States.DATA: [MessageHandler(Filters.text, setup_conv.data)],
        States.FINISHED: [MessageHandler(Filters.text, setup_conv.finished)],
    },
    fallbacks=[CommandHandler('cancel', setup_conv.cancel_setup),
            CommandHandler('start', setup_conv.chart_type)],
    persistent=False,
    per_message=False,
    per_user=True,
    conversation_timeout=120.0,
)

# asks the user what chart to show
def chart(update: Update, context: CallbackContext) -> None:
    if context.user_data:
        update.message.reply_text(
            text=f"Hello {update.effective_user.first_name} 👋, here is your {context.user_data['chart']} chart"
        )

        chart=Chart(
            data = [context.user_data['data']], 
            timeframe = context.user_data['tf'], 
            c_type = context.user_data['chart'], 
            region = context.user_data['region'])

        try:
            path = chart.plot()
            context.bot.send_photo(update.effective_chat.id, open(path,'rb'))
        except DataException:
            update.message.reply_text(
                'Wir haben leider nicht genug Daten für diesen Zeitraum\.\n`cases` kannst du immer verwenden, `deaths` und `incidence` sind jedoch nicht vollsträndig verfügbar', parse_mode=ParseMode.MARKDOWN_V2)
    else:
        reply_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("line", callback_data='line')],
            [InlineKeyboardButton("bar", callback_data='bar')],
            [InlineKeyboardButton("geo", callback_data='geo')],
        ])
        update.message.reply_text(
            f'Hello {update.effective_user.first_name} 👋, please choose a chart:',
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

    chart=Chart(
        data = ['cases'], 
        timeframe = '3W', 
        c_type = update.callback_query.data,
        region = 'Sachsen')
    
    try:
        path = chart.plot()
        context.bot.send_photo(update.effective_chat.id, open(path,'rb'))
    except DataException:
        update.message.reply_text(
            'Wir haben leider nicht genug Daten für diesen Zeitraum\.\n`cases` kannst du immer verwenden, `deaths` und `incidence` sind jedoch nicht vollsträndig verfügbar', parse_mode=ParseMode.MARKDOWN_V2)

# returns the latest information in a simple overview
def status(update: Update, context: CallbackContext) -> None:
    # TODO: Buid Module to handle
    df = pd.read_csv('./data/covid_de.csv')

    tf = df[df['date'] >= df['date'].max()]

    aggregation_functions = {'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    aggregation_functions_state = {'state': 'first', 'cases': 'sum', 'deaths': 'sum', 'recovered': 'sum'}
    germany =  tf.groupby(tf['date']).aggregate(aggregation_functions)
    state =  tf.groupby(tf['state']).aggregate(aggregation_functions_state)
    
    update.message.reply_text(f"New infections in Germany: {germany['cases'].values[0]}\nNew infections in Saxony: {state.loc[state.index=='Sachsen']['cases'].values[0]}") 

def news(update: Update, context: CallbackContext) -> None:
    auth = tweepy.OAuthHandler(os.getenv('TWITTER_KEY'), os.getenv('TWITTER_SECRET'))
    auth.set_access_token(os.getenv('TWITTER_AT'), os.getenv('TWITTER_ATS'))

    api = tweepy.API(auth)

    public_tweets = api.user_timeline('@rki_de', count=10)

    id = random.randint(0, 10)

    update.message.reply_text(f'Twitter sagt:\n{public_tweets[id].text}\n\nhttps://twitter.com/{public_tweets[id].user.screen_name}/status/{public_tweets[id].id}')

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                    text='Automatic updates have been enabled.')

    context.job_queue.run_daily(status, time=datetime.time(15, 0, 0), context=update.message.chat_id, name='update')

def stop(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                    text='Automatic updates have been disabled.')
    context.job_queue.stop()

def sources(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'My data comes from the RKI and is Updated daily.\nA great overview of this data can be found here: https://npgeo-corona-npgeo-de.hub.arcgis.com\n\nThis is the link to the dataset: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/23b1ccb051f543a5b526021275c1c6e5_0')

def reset(update: Update, context: CallbackContext) -> None:
    context.user_data.clear()

    update.message.reply_text("Ok ich habe deine Einstellungen zurückgesetzt. Du kannst sie jederzeit mit /setup neu konfigurieren.")

handlers = [
    setup_handler,
    CommandHandler('start', start, pass_job_queue=True),
    CommandHandler('stop', stop, pass_job_queue=True),
    CommandHandler('chart', chart),
    CallbackQueryHandler(chart_answer),
    CommandHandler('status', status),
    CommandHandler('news', news),
    CommandHandler('sources', sources),
    CommandHandler('reset', reset),
]
