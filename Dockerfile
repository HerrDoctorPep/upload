FROM python:3.10-slim AS baseimage

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN set -ex \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-extra \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

FROM baseimage AS deploycontainer

ADD . /uploadapp/
WORKDIR /uploadapp

RUN pip install -r /uploadapp/requirements.txt

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]
