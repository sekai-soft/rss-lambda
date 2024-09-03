FROM python:3.12-slim-bullseye

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn==22.0.0

COPY . /app

ENTRYPOINT ["/app/run.sh"]
