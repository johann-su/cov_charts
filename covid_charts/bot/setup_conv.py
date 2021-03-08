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
        return States.STATE
    else:
        update.message.reply_text(f"Please select one of the options below")
        return States.CHART_TYPE

def state(update: Update, context: CallbackContext) -> str:
    regex = r'[0-9][0-9]?(D|W|M|Y)'
    # set data from prev step
    if re.match(regex, update.message.text):
        context.user_data['tf'] = update.message.text

        update.message.reply_text(f"Now tell me in which state you live. I won't tell anyone. Promise :) \n If you want to look at the whole country just type Germany.")
        return States.COUNTY
    else:
        update.message.reply_text(f"Nah you cant fool me by sending your timeframe in the wron format. Try again!")
        return States.TIMEFRAME

def county(update: Update, context: CallbackContext) -> str:
    if update.message.text in choices_state:
        if update.message.text != 'Germany':
            context.user_data['state'] = update.message.text
        else:
            context.user_data['state'] = None

        update.message.reply_text(f"If you want to focus on a county you can do so. Just type in your county in the following format: SK Dresden, LK Bautzen etc. You can also skip with the /skip command")
        return States.DATA
    else:
        update.message.reply_text(f"The state you said you live in dosn't exist anywhere in Germany. You can't trick me.\nTry again!")
        return States.STATE

def data(update: Update, context: CallbackContext) -> str:
    if update.message.text in choices_county or update.message.text == '/skip':
        if update.message.text != '/skip':
            context.user_data['county'] = update.message.text
        else:
            context.user_data['county'] = None

        update.message.reply_text(f"Last Question: What data do you want to see? I can offer cases, deaths or the seven day incidence. If you want to see multiple data points you can seperate them with a ','")
        return States.FINISHED
    else:
        update.message.reply_text(f"The county you told me dosn't exist anywhere in Germany. You can't trick me.\nTry again!")
        return States.COUNTY

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