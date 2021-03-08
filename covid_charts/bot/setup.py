from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from covid_charts.bot.state import States

def chart_type(update: Update, context: CallbackContext) -> str:
    reply_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("line", callback_data='line')],
        [InlineKeyboardButton("bar", callback_data='bar')],
        [InlineKeyboardButton("geo", callback_data='geo')],
    ])
    update.message.reply_text(
        'Lets start with an easy question: What chart would you like?',
        reply_markup=reply_buttons
    )
    return State.TIMEFRAME

def timeframe(update: Update, context: CallbackContext) -> str:
    # Must call answer!
    update.callback_query.answer()

    # set data from prev step
    context.user_data['chart'] = update.callback_query.data

    update.message.reply_text(f"So you like {context.user_data['chart']} charts? Good choice!\n\nNext tell me what timeframe you want? Valid Formats are 1D, 1W, 1Y etc.",
                              reply_markup=ForceReply())
    return State.STATE

def state(update: Update, context: CallbackContext) -> str:
    # set data from prev step
    if
    context.user_data['timeframe'] = update.message.text

    update.message.reply_text(f"Now tell me in which state you live. I won't tell anyone. Promise :) \n If you want to look at the whole country just type Germany.",
                              reply_markup=ForceReply())
    return State.COUNTY

def county(update: Update, context: CallbackContext) -> str:
    update.message.reply_text(f"If you want to focus on a county you can do so. Just type in your county in the following format: SK Dresden, LK Bautzen etc.",
                              reply_markup=ForceReply())
    return State.DATA

def data(update: Update, context: CallbackContext) -> str:
    update.message.reply_text(f"Last Question: What data do you want to see? I can offer cases, deaths or the seven day incidence. If you want to see multiple data points you can seperate them with a ','",
                              reply_markup=ForceReply())
    return State.FINISHED

def finished(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Your through. I will remember your configuration but you can change it whenever you want.")
    return State.CHART_TYPE

def cancel_setup(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("You canceled the setup :(")
    return State.CHART_TYPE
