FROM python:3-windowsservercore

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./etl etl
COPY utils etl/utils

# Copy static db file to container if exists. This makes the db read-only and is not practical for prod.
COPY . app.db* etl/

WORKDIR etl