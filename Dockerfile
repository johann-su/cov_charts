FROM python:3.8
WORKDIR /corona-charts
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "."]