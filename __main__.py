import logging
import os
import atexit

from covid_charts.bot import bot
from covid_charts import cronjobs
from covid_charts.bot.handlers import handlers

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n', level=logging.INFO, filename='./logs/logFile.log')

if __name__ == '__main__':
    token = os.environ['TELEGRAM_TOKEN']
    bot.run(token=token, handlers=handlers)
    cronjobs.start()
    atexit.register(cronjobs.stop())