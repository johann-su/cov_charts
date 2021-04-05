import os
import random
import time
import pandas as pd
from datetime import datetime

from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler, CallbackContext

from covid_charts.bot.state import States
from covid_charts.bot import setup_conv
from covid_charts.bot import bot
from covid_charts.bot.utils import is_sender_admin
from covid_charts.charts import Chart
from covid_charts.exceptions import DataException

import sqlite3 as sql

from covid_charts import collect_news

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
    if is_sender_admin(update.message, context.bot):
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
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

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
    with sql.connect('./data/covid.db') as con:
        c = con.cursor()
        brd = c.execute("SELECT cases, cases_new FROM covid_germany WHERE date >= :timeframe AND region = 'Bundesrepublik Deutschland'", {
            'timeframe': time.mktime((datetime.now() - pd.Timedelta('1D')).timetuple())
        }).fetchone()
        sachsen = c.execute("SELECT cases, cases_new, incidence FROM covid_germany WHERE date >= :timeframe AND region = 'Sachsen'", {
            'timeframe': time.mktime((datetime.now() - pd.Timedelta('1D')).timetuple())
        }).fetchone()

    update.message.reply_text(
        f"Infektionen in Deutschland: {brd[0]:n}\nNeue Infektionen in Deutschland: {brd[1]:n}\n\nInfektionen in Sachsen: {sachsen[0]:n}\nNeue Infektionen in Sachsen: {sachsen[1]:n}\nSieben Tage Inzidenz in Sachsen: {sachsen[2]:n}")

def news(update: Update, context: CallbackContext) -> None:
    if is_sender_admin(update.message, context.bot):
        zeit = collect_news.get_articles()

        update.message.reply_text(
            f"""Hier sind ein paar interessante Artikel aus der Zeit zu Covid:
            \n{zeit[0]['title']}\n{zeit[0]['subtitle']}\nLink {zeit[0]['href']}
            \n\n{zeit[1]['title']}\n{zeit[1]['subtitle']}\nLink {zeit[1]['href']}
            \n\n{zeit[2]['title']}\n{zeit[2]['subtitle']}\nLink {zeit[2]['href']}""")
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

def start(update, context):
    if is_sender_admin(update.message, context.bot):
        context.bot.send_message(chat_id=update.message.chat_id,
                    text='Automatic updates have been enabled.')
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

    context.job_queue.run_daily(status, time=datetime.time(15, 0, 0), context=update.message.chat_id, name='update')

def stop(update, context):
    if is_sender_admin(update.message, context.bot):
        context.bot.send_message(chat_id=update.message.chat_id,
                        text='Automatic updates have been disabled.')
        context.job_queue.stop()
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

def sources(update: Update, context: CallbackContext) -> None:
    if is_sender_admin(update.message, context.bot):
        update.message.reply_text(f'My data comes from the RKI and is Updated daily.\nA great overview of this data can be found here: https://npgeo-corona-npgeo-de.hub.arcgis.com\n\nThis is the link to the dataset: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/23b1ccb051f543a5b526021275c1c6e5_0')
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

def reset(update: Update, context: CallbackContext) -> None:
    if is_sender_admin(update.message, context.bot):
        context.user_data.clear()

        update.message.reply_text("Ok ich habe deine Einstellungen zurückgesetzt. Du kannst sie jederzeit mit /setup neu konfigurieren.")
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

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
