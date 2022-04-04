FROM python:3-windowsservercore

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./api api
COPY utils api/utils

# Copy static db file to container if exists. This makes the db read-only and is not practical for prod.
COPY . app.db* api/

WORKDIR api