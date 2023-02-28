# Dockerfile that will run NGINX as a service for our project inside our directory.

# Kateri base docker image bomo uporabili (od nginx)
# OPOMBA:   Lahko bi napisali tudi samo FROM nginx --> in bi uporabili default NGINX image (z neta)
#           However, by default, that container runs in root mode, so it runs in the root or the most privileged user.
#           That is not best practice for security.
#           For security purposes, you want to make sure your application is running with the least privileges
#           that it needs in order to perform its application duties.
#           So our Engine X doesn't need to have a root user account because all we need to do is get to run it
#           and give it access to a specific directory to be able to handle requests from that directory.
FROM nginxinc/nginx-unprivileged:1-alpine

# Maintainer == to so samo metapodatki o image-u (ki se bo naredil iz tega dockerfile-a)
LABEL maintainer="minoa.si"

# Kopiramo file iz hosta v docker image
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# we're defining some environment variables here.
# So these are default values for our containers.
# Environment variables are running from this image.
# So if you don't specify an override, then this will be what the defaults are and we're going to listen
# on Port 8000.
ENV LISTEN_PORT=8000

# That's the hostname where our uWSGI app is running.
ENV APP_HOST=app

# This is the port value whiskey amp is going to run on, which is going to be port 9000.
ENV APP_PORT=9000

# We are switching to the root user here.
# OPOMBA:
#       And as I mentioned previously, you don't want to run your application as a user, but you do need to
#       switch to the root user in order to set up your image to get it ready.
USER root


# So we're going to need to be the route user in order to run these commands bellow.
#
#   We create a new directory which is going to be user to store the static files
RUN mkdir -p /vol/static && \
    # chmod == change mode --> spreminjamo pravice na tem direktoriju
    # So that we can read the contents from the static file.
    chmod 755 /vol/static && \

    # The reason we need to do this is because we need to be able to set permissions on this file so our nginx
    # user can modify it. Because when we execute our run or .sh scripts, we're going to be calling this
    # and substitute command and that's going to require that our user has right access to this file in order
    # to override the contents.
    # Touch just creates an empty file on a given location. The only purpose of this is to give it ownership on the next line.
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \

    # we're adding execute permission to our run go SRH
    # script, which is required for our Docker container to be able to run this script.
    chmod +x /run.sh

# Here we're setting up a volume for such slash static, so it's the default volume that's going to be
# created for this image.
#
# And later on we're going to be mapping this volume using our Docker compose configuration.
VOLUME /vol/static

# So this then switches to the engine user.
# So we're no longer as the root user.
#
# And whatever user is the last user to switch to when we're building our docket image will be the user
# that is used to run the application.
USER nginx

# So this is the default script that's going to be run when you create instances from this image and we're
# simply calling our run to our site scripts that we copied to the image further above.
CMD ["/run.sh"]