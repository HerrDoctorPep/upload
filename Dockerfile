FROM python:3.10 AS baseimage

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

FROM baseimage AS deploycontainer

ADD . /uploadapp/
WORKDIR /uploadapp

RUN pip install -r /uploadapp/config/requirements.txt

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]
