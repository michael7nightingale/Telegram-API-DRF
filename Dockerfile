FROM python:3.11

COPY . .

WORKDIR ./server

RUN pip install -r /requirements.txt

EXPOSE 8008
