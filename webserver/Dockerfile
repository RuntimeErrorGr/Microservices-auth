FROM python:3.12-alpine

RUN mkdir -p /webserver
WORKDIR /webserver

RUN apk add --no-cache curl bash

RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN pip install -r requirements.txt
COPY . /webserver

RUN chmod +x entrypoint.sh

EXPOSE 5000

CMD ["./entrypoint.sh"]