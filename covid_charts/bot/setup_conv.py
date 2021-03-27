import re

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from covid_charts.bot.state import States

from covid_charts.vars import choices_state, choices_county

def chart_type(update: Update, context: CallbackContext) -> str:
    chart_buttons = ReplyKeyboardMarkup([
        [KeyboardButton("line", callback_data='line'), KeyboardButton("bar", callback_data='bar')],
        [KeyboardButton("geo", callback_data='geo')],
    ],
    one_time_keyboard=True)
    update.message.reply_text(
        'Lets start with an easy question: What chart would you like?',
        reply_markup=chart_buttons
    )

    return States.TF

def timeframe(update: Update, context: CallbackContext) -> str:
    regex = r'(line|bar|geo)'
    # set data from prev step
    if re.match(regex, update.message.text):
        context.user_data['chart'] = update.message.text

        update.message.reply_text(f"So you like {context.user_data['chart']} charts? Good choice!\n\nNext tell me what timeframe you want? Valid Formats are 1D, 1W, 1Y etc.")
        return States.REGION
    else:
        update.message.reply_text(f"Please select one of the options below")
        return States.CHART_TYPE

def region(update: Update, context: CallbackContext) -> str:
    regex = r'[0-9][0-9]?(D|W|M|Y)'
    # set data from prev step
    if re.match(regex, update.message.text):
        context.user_data['tf'] = update.message.text

        update.message.reply_text(f"Now tell me in which area you want to see")
        return States.DATA
    else:
        update.message.reply_text(f"Nah you cant fool me by sending your timeframe in the wrong format. Try again!")
        return States.TIMEFRAME

def data(update: Update, context: CallbackContext) -> str:
    if update.message.text in choices_county or update.message.text in choices_State or update.message.text == 'Bundesrepublik Deutschland':
        context.user_data['region'] = update.message.text

        update.message.reply_text(f"Last Question: What data do you want to see? I can offer **cases**, **deaths** or the seven day **incidence**. If you want to see multiple data points you can seperate them with a ','")
        return States.FINISHED
    else:
        update.message.reply_text(f"The region you told me dosn't exist anywhere in Germany.\nTry again!")
        return States.REGION

def finished(update: Update, context: CallbackContext) -> None:
    regex=r'(cases|deaths|incidence),?(cases|deaths|incidence)?,?(cases|deaths|incidence)?'
    if re.match(regex, update.message.text):
        context.user_data['data'] = update.message.text

        update.message.reply_text(f"Thats all. I will remember your configuration but you can change it whenever you want.")
        return States.END
    else:
        update.message.reply_text(f"The data you told me was not in a correct shape or contained unknown datatypes. Don't try to mess with me ok?\nTry again!")
        return States.DATA

def cancel_setup(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("You canceled the setup :(")
    return States.END

def skip_county(update: Update, context: CallbackContext) -> str:
    return States.DATA