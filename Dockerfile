FROM python:3.5
COPY app/requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY app /app
WORKDIR /app
CMD ["uwsgi", "uwsgi.ini"]
