import logging
from crontab import CronTab

LOGGER = logging.getLogger(__name__)

cron = CronTab(user='root')
job = cron.new(command='python collect_data.py')
job.hour.on(0)
job.enable(False)
cron.write()

def start():
    job.enable()

def stop():
    job.enable(False)