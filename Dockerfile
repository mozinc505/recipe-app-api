FROM python:3.9-alpine3.13

#Kdo bo vzdrževal ta docker image, ki bo narejen na osnovi tega docker file-a
LABEL maintainer="minoa.si"

#Priporočljivo, ko uporabljaš python znotraj containerja
ENV PYTHONUNBUFFERED 1

#VIRTUAL ENVIRONMENT
#We can replace activate venv by setting the appropriate environment variables: VIRTUAL_ENV and PATH
#ENV VIRTUAL_ENV=/py
#ENV PATH="/scripts:$VIRTUAL_ENV/bin:$PATH"

#Komanda s katero kopiramo datoteke iz docker hosta (mac ali pc) v docker image.
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# WSGI
# So the reason for this is we're going to be creating a directory in our project called Scripts that
# are going to be used for creating help scripts that are run by our Docker application.
COPY ./scripts /scripts

#Kopiramo direktorij na računalniku v docker-image (container)
COPY ./app /app
#Privzeti direktorij na katerem se bodo izvajali ukazi (commands) ko bomo izvajali komande na docker-image
WORKDIR /app
#Določimo preko katerega porta bomo komunicirali s containerjem
#S tem ukazom (EXPOSE) odpremo port drugim docker containerjem
#Na ta način določimo kateri port container posluša
EXPOSE 8000

ARG DEV=false

#Uporabimo RUN commando s katero inštaliramo aplikacije in packages, ki želimo da so del image-a.
#OPOMBA: Komande se izvedejo samo, ko kreiramo docker image (Docker build)
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # inštaliramo postgres client paket - ta mora ostati tudi v produkciji
    # paket, ki ga moramo inštalirati v alpine image-u, da dodamo podporo za postgres

    #OPOMBA: Kar potrebujemo stalno v dockerju --> dodamo v to naslednjo vrstico
    apk add --update --no-cache postgresql-client jpeg-dev && \

    #OPOMBA: Kar potrebujemo samo ob namestitvi določenih stvari (in jih bomo spodaj odstranili)  damo v tole spodnjo vrstico.
    # nastavi navidezno odvisnost med paketi (jih grupira skupaj - da jih kasneje lažje odstranimo)
    apk add --update --no-cache --virtual .tmp-build-deps \
        # povemo katere pakete potrebujemo za inštaliranje postgres adapterja
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
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
        django-user && \
    # naredimo direktorij (parameter -p uporabimo, da naredi vse poddirektorije v direktoriju, ki smo ga specificirali)
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    # sprememnimo lastnika direktorija vol in vseh pod-direktorijev (chown --> change owner, -R == recursive)
    # So we're setting the owner to Django user and the group to Django user.
    # Razlog: da bo imel django-user pravico spreminjati vsebino direktorija, ko se bo aplikacija izvajala
    chown -R django-user:django-user /vol && \
    # chmod == change mode --> spreminjamo pravice na tem direktoriju
    chmod -R 755 /vol && \
    # WSGI
    # This just makes sure that our scripts directory is executable because we need to be able to execute the scripts inside this directory.
    chmod -R +x /scripts


#ENV PATH="/py/bin:$PATH"
ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

# That's going to be the name of the script that we're going to create that runs our application.

# So the command here, the bottom is the default command that's run for docker containers that are spawned
# from our image that's built from this Docker file.

# You can override this using Docker compose, and we will be overriding it for our development server
# because our development server is going to be using our managed API run server command instead of WSGI.
#
# The CMD command tells Docker how to run the application we packaged in the image.
CMD ["run.sh"]

#Navodila: https://linuxhint.com/understand_dockerfile/
