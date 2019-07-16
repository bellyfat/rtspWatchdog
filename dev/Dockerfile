FROM ubuntu:bionic
MAINTAINER Lucas Zanella (me@lucaszanella.com)

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3 python3-pip

RUN pip3 install --pre rx && pip3 install --upgrade onvif_zeep

ENTRYPOINT "/home/watchdog.py"
