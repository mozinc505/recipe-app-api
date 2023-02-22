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

    #OPOMBA: Kar potrebujemo stalno v dockerju --> dodamo v to naslednjo vrstico
    apk add --update --no-cache postgresql-client jpeg-dev && \

    #OPOMBA: Kar potrebujemo samo ob namestitvi določenih stvari (in jih bomo spodaj odstranili)  damo v tole spodnjo vrstico.
    # nastavi navidezno odvisnost med paketi (jih grupira skupaj - da jih kasneje lažje odstranimo)
    apk add --update --no-cache --virtual .tmp-build-deps \
        # povemo katere pakete potrebujemo za inštaliranje postgres adapterja
        build-base postgresql-dev musl-dev zlib zlib-dev && \
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
        django-user && \
    # naredimo direktorij (parameter -p uporabimo, da naredi vse poddirektorije v direktoriju, ki smo ga specificirali)
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    # sprememnimo lastnika direktorija vol in vseh pod-direktorijev (chown --> change owner, -R == recursive)
    # So we're setting the owner to Django user and the group to Django user.
    # Razlog: da bo imel django-user pravico spreminjati vsebino direktorija, ko se bo aplikacija izvajala
    chown -R django-user:django-user /vol && \
    # chmod == change mode --> spreminjamo pravice na tem direktoriju
    chmod -R 755 /vol


#ENV PATH="/py/bin:$PATH"

USER django-user

#Navodila: https://linuxhint.com/understand_dockerfile/
