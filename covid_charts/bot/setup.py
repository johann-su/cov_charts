import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import CallbackContext
from covid_charts.bot.state import States

from covid_charts.vars import choices_state, choices_county

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
    regex = r'[0-9][0-9]?(D|W|M|Y)'
    # set data from prev step
    if re.match(regex, update.message.text):
        context.user_data['tf'] = update.message.text

        update.message.reply_text(f"Now tell me in which state you live. I won't tell anyone. Promise :) \n If you want to look at the whole country just type Germany.",
                              reply_markup=ForceReply())
        return State.COUNTY
    else:
        update.message.reply_text(f"Nah you cant fool me by sending your timeframe in the wron format. Try again!",
                              reply_markup=ForceReply())
        return State.TIMEFRAME

def county(update: Update, context: CallbackContext) -> str:
    if update.message.text in choices_state:
        context.user_data['state'] = update.message.text

        update.message.reply_text(f"If you want to focus on a county you can do so. Just type in your county in the following format: SK Dresden, LK Bautzen etc.",
                                reply_markup=ForceReply())
        return State.DATA
    else:
        update.message.reply_text(f"The state you said you live in dosn't exist anywhere in Germany. You can't trick me.\nTry again!",
                                reply_markup=ForceReply())
        return State.STATE

def data(update: Update, context: CallbackContext) -> str:
    if update.message.text in choices_county:
        context.user_data['county'] = update.message.text

        update.message.reply_text(f"Last Question: What data do you want to see? I can offer cases, deaths or the seven day incidence. If you want to see multiple data points you can seperate them with a ','",
                                reply_markup=ForceReply())
        return State.FINISHED
    else:
        update.message.reply_text(f"The county you told me dosn't exist anywhere in Germany. You can't trick me.\nTry again!",
                                reply_markup=ForceReply())
        return State.COUNTY

def finished(update: Update, context: CallbackContext) -> None:
    regex=r'(cases|deaths|incidence),?(cases|deaths|incidence)?,?(cases|deaths|incidence)?'
    if re.match(regex, update.message.text):
        context.user_data['data'] = update.message.text

        update.message.reply_text(f"Thats all. I will remember your configuration but you can change it whenever you want.")
        return State.CHART_TYPE
    else:
        update.message.reply_text(f"The data you told me was not in a correct shape or contained unknown datatypes. Don't try to mess with me ok?\nTry again!")
        return State.CHART_TYPE

def cancel_setup(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("You canceled the setup :(")
    return State.CHART_TYPE
