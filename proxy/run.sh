#!/bin/sh

# shell script that's going to be used to start our proxy service.

# Odpremo transakcijo (da se skripta ne izvede, če karkoli v skipti ne gre skozi)
set -e

# environment substitute
#
# We are inserting template file s pravim (v template file-u nastavimo vse ENV variable)
#
# And what this does is is substitute all of the syntax in default.conf.tpl file.
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

## And what this does is it starts engine X with the configuration that we've just set here.
# So we're passing it through and substitute and we're outputting it.
# And for such aa /etc/nginx/conf.d/default.conf --- that's the default location for
# the default configuration of engine x.
# And then when we start the server, it's going to have this configuration and we're passing in Damon off.
# And all that means is that we want to run engine X in the foreground.
#
#
# So usually when you start ngnix on a server, it will be running in the background and then you can
# interact with it through some kind of service manager.
# Because we're running this in a Docker container, we want to make sure the service is running in the foreground.
# Which means it is at the forefront of the running application.
# It is the primary thing being run by that Docker container. And this way all of the logs and everything
# get output to the screen and the Docker container will continue to run while the ngnix server is
# running.
# So until you kill the ngnix server, the Docker container is going to continue to run.
nginx -g 'daemon off;'