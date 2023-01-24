FROM python:3.9-alpine3.13
LABEL maintainer="minoa.si"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # inštaliramo postgres client paket - ta mora ostati tudi v produkciji 
    # paket, ki ga moramo inštalirati v alpine image-u, da dodamo podporo za postgres
    apk add --update --no-cache postgresql-client && \ 
    # nastavi navidezno odvidnost med paketi (jih grupira skupaj - da jih kasneje lažje odstranimo)
    apk add --update --no-cache --virtual .tmp-build-deps \ 
        # povemo katere pakete potrebujemo za inštaliranje postgres adapterja
        build-base postgresql-dev musl-dev && \ 
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    # odstranimo pakete, ki smo jih zgoraj dodali (jih pocistimo)
    # pocistimo jih, ker jih potrebujemo samo za namestitev postgresql-clienta, ne pa za delovanje.
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"

USER django-user
