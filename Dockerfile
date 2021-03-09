FROM python:3.8
WORKDIR /corona-charts
COPY . .
ENV PROJ_DIR=/corona-charts/
RUN apt-get install libgeos-dev
RUN pip install -r requirements.txt
CMD ["python", "."]