from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

from covid_charts.bot.state import States
from covid_charts.bot import setup

conv_handler = ConversationHandler(
    name='setup_handler',
    entry_points=[CommandHandler('setup', chart_type)],
    states={
        States.CHART_TYPE: [CallbackQueryHandler(setup.chart_type)],
        States.TIMEFRAME: [MessageHandler(Filters.text, setup.timeframe)],
        States.STATE: [MessageHandler(Filters.text, setup.state)],
        States.COUNTY: [MessageHandler(Filters.text, setup.county)],
        States.DATA: [MessageHandler(Filters.text, setup.data)],
        States.FINISHED: [MessageHandler(Filters.text, setup.finished)],
    },
    persistent=True,
    fallbacks=[CommandHandler('cancel', cancel_setup),
            CommandHandler('start', chart_type)]
)

# asks the user what chart to show
def chart(update: Update, context: CallbackContext) -> None:
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
    # configure chart
    if context.user_data:
        chart=Chart(
            data = context.user_data['data'], 
            timeframe = context.user_data['tf'], 
            c_type = context.user_data['chart'], 
            state = context.user_data['state'], 
            county = context.user_data['county'])
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

def sources(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'My data comes from the RKI and is Updated daily.\nA great overview of this data can be found here: https://npgeo-corona-npgeo-de.hub.arcgis.com\n\nThis is the link to the dataset: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/23b1ccb051f543a5b526021275c1c6e5_0')

def news(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('There are currently no news to show')

handlers = [
    CommandHandler('stats', show_stats),
    CallbackQueryHandler(process_inline_button_click),
    InlineQueryHandler(inline_find_post),
    conv_handler
]