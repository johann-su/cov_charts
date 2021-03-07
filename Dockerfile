FROM python:3.8
COPY . .
RUN pip install -r requirements.txt
RUN crontab mycronjobs.txt
CMD ["python", "./bot.py"]