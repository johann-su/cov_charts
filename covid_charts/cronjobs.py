from crontab import CronTab
cron = CronTab(user='root')
job = cron.new(command='python collect_data.py')
job.hour.on(0)
cron.write()