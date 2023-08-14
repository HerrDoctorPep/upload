FROM python:3.10-slim AS baseimage

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update -q && \
    apt-get install -q -y --no-install-recommends \
    wget \ 
    ffmpeg \
    libavcodec-extra

# Roll back to openssl 1.1.1
RUN wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb \
    && dpkg -i libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb

RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM baseimage AS deploycontainer

COPY requirements.txt /requirements.txt 

RUN pip install -r /requirements.txt

ADD . /uploadapp/
WORKDIR /uploadapp

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]
