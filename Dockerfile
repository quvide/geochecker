FROM python:3.12.0-alpine

WORKDIR /app

RUN apk add --no-cache build-base linux-headers

COPY app/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY app /app

CMD ["uwsgi", "uwsgi.ini"]
