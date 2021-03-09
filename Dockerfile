FROM python:3.8

ENV PROJ_DIR=/corona-charts

RUN apt-get update
RUN apt-get install libgeos-dev proj-bin -y

WORKDIR /corona-charts

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "."]