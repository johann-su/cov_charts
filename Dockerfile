FROM python:3.8
WORKDIR /telegram_bot
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]