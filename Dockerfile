FROM python:3.11

RUN apt-get update && apt-get install -y vim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/app

CMD ["gunicorn", "--conf", "app/gunicorn_conf.py","--bind", "0.0.0.0:8080", "app.app:app"]
