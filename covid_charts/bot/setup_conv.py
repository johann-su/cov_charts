import re

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import CallbackContext
from covid_charts.bot.state import States

from covid_charts.vars import choices_state, choices_county

def chart_type(update: Update, context: CallbackContext) -> str:
    if is_sender_admin(update.message, context.bot):
        chart_buttons = ReplyKeyboardMarkup([
            [KeyboardButton("line", callback_data='line'), KeyboardButton("bar", callback_data='bar')],
            [KeyboardButton("geo", callback_data='geo')],
        ], one_time_keyboard=True)
        update.message.reply_text(
            'Das wichtigste zuerst: Welches Chart gefällt dir am besten?',
            reply_markup=chart_buttons
        )

        return States.TF
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

def timeframe(update: Update, context: CallbackContext) -> str:
    if is_sender_admin(update.message, context.bot):
        regex = r'(line|bar|geo)'
        # set data from prev step
        if re.match(regex, update.message.text):
            context.user_data['chart'] = update.message.text

            update.message.reply_text(f"{context.user_data['chart']} charts? 👍\n\nAls nächstes brauche ich einen Zeitraum für den du Infos haben möchtest\.\n`7D` \= eine Woche, `4W` \= ein Monat, `52W` \= ein Jahr usw\.", reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN_V2)
            return States.REGION
        else:
            update.message.reply_text("Huch 🤔\nDamit kann ich nichts anfangen\n\nBitte wähle ein Chart aus der Liste")
            return States.CHART_TYPE
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

def region(update: Update, context: CallbackContext) -> str:
    if is_sender_admin(update.message, context.bot):
        regex = r'[0-9][0-9]?[0-9]?(D|W)'
        # set data from prev step
        if re.match(regex, update.message.text):
            context.user_data['tf'] = update.message.text

            update.message.reply_text(
                "Welche Region möchtest du sehen? Die `Bundesrepublik Deutschland`, `Sachsen` oder doch lieber nur `Dresden`?\n\n**Wenn du ein geo chart haben möchtest kannst du nicht daten auf Landkreisebene anfordern\!**", parse_mode=ParseMode.MARKDOWN_V2)
            return States.DATA
        else:
            update.message.reply_text(
                "Huch 🤔\nDamit kann ich nichts anfangen\n\nZur Erinnerung: Das Format war `7D` \= eine Woche, `4W` \= ein Monat, `52W` \= ein Jahr usw\.", parse_mode=ParseMode.MARKDOWN_V2)
            return States.TIMEFRAME
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")
    
def data(update: Update, context: CallbackContext) -> str:
    if is_sender_admin(update.message, context.bot):
        if update.message.text in choices_county or update.message.text in choices_state or update.message.text == 'Bundesrepublik Deutschland':

            context.user_data['region'] = update.message.text

            update.message.reply_text("Letzte Frage: Welche Daten möchtest du sehen?\nIch kann dir Infos über die Infektionen und Tote geben\.\n\n`cases` \= Infektionen, `deaths` \= Tote\, `incidence` \= 7\-Tage\-Inzidenz\.\n**Tipp:** Du kannst auch mehrere Werte sehen indem du die Werte mit einem Komma trennst", parse_mode=ParseMode.MARKDOWN_V2)
            return States.FINISHED
        else:
            valid_choices = choices_county.append(choices_State)
            valid_choices = choices_county.append('Bundesrepublik Deutschland')
            suggestion = difflib.get_close_matches(update.message.text, valid_choices)
            print(suggestion)
            update.message.reply_text(f"Huch 🤔\nDamit kann ich nichts anfangen\n\nMeintest du vlt. {suggestion}?")
            return States.REGION
    else:
        update.message.reply_text(
            "Du bist nicht der Admin der Gruppe und kannst daher keine Commands an den Bot senden.\nDu kannst mich zu deinen Kontakten hinzufügen https://t.me/CovGermanyBot um alle Funktionen nutzen zu können")

def finished(update: Update, context: CallbackContext) -> None:
    regex=r'(cases|deaths),? ?(cases|deaths)?'
    if re.match(regex, update.message.text):
        context.user_data['data'] = update.message.text

        update.message.reply_text("Das war alles 👍. Ich merke mir deine Einstellungen, aber du kannst sie jederzeit mit /setup wieder ändern.")
        return States.END
    else:
        update.message.reply_text("Huch 🤔\nDamit kann ich nichts anfangen\n\nZur Erinnerung: Die Daten können `cases` und `deaths` sein und müssen mit einem , getrennt werden")
        return States.DATA

def cancel_setup(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Du hast das Setup abgebrochen. Bis zum nächsten mal 👋")
    return States.END
