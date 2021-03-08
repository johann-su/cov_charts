import logging
import covid_charts.bot

from covid_charts.bot.handlers import handlers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n', level=logging.INFO)

if __name__ == '__main__':
    token = os.environ['TELEGRAM_TOKEN']
    bot.run(token=token, handlers=handlers)