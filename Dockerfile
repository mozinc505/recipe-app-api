FROM python:3.9-alpine3.13

#Kdo bo vzdrževal ta docker image, ki bo narejen na osnovi tega docker file-a
LABEL maintainer="minoa.si"

#Priporočljivo, ko uporabljaš python znotraj containerja
ENV PYTHONUNBUFFERED 1

#VIRTUAL ENVIRONMENT
#We can replace activate venv by setting the appropriate environment variables: VIRTUAL_ENV and PATH
ENV VIRTUAL_ENV=/py
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

#Komanda s katero kopiramo datoteke iz docker hosta (mac ali pc) v docker image.
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
#Kopiramo direktorij na računalniku v docker-image (container)
COPY ./app /app
#Privzeti direktorij na katerem se bodo izvajali ukazi (commands) ko bomo izvajali komande na docker-image
WORKDIR /app
#Določimo preko katerega porta bomo komunicirali s containerjem
#S tem ukazom (EXPOSE) odpremo port drugim docker containerjem
EXPOSE 8000

ARG DEV=false

#Uporabimo RUN commando s katero inštaliramo aplikacije in packages, ki želimo da so del image-a.
#OPOMBA: Komande se izvedejo samo, ko kreiramo docker image (Docker build)
RUN python -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip && \
    # inštaliramo postgres client paket - ta mora ostati tudi v produkciji
    # paket, ki ga moramo inštalirati v alpine image-u, da dodamo podporo za postgres
    apk add --update --no-cache postgresql-client && \
    # nastavi navidezno odvidnost med paketi (jih grupira skupaj - da jih kasneje lažje odstranimo)
    apk add --update --no-cache --virtual .tmp-build-deps \
        # povemo katere pakete potrebujemo za inštaliranje postgres adapterja
        build-base postgresql-dev musl-dev && \
    $VIRTUAL_ENV/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then $VIRTUAL_ENV/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    # odstranimo pakete, ki smo jih zgoraj dodali (jih pocistimo)
    # pocistimo jih, ker jih potrebujemo samo za namestitev postgresql-clienta, ne pa za delovanje.
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user


#ENV PATH="/py/bin:$PATH"

USER django-user

#Navodila: https://linuxhint.com/understand_dockerfile/
