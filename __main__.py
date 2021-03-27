import logging
import os
import atexit
import schedule
import time

from covid_charts.bot import bot
from covid_charts import collect_data
from covid_charts.bot.handlers import handlers

from dotenv import load_dotenv
load_dotenv(override=True)

from covid_charts.charts import Chart

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n', level=logging.INFO, filename='./logs/logFile.log')

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_TOKEN')
    bot.run(token=token, handlers=handlers)
    schedule.every().day.at("00:00").do(collect_data.collect)