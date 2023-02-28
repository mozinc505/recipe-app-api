#!/bin/sh

# With statement above --> We are marking our file as a "shell script file"
#So, by default, it will be run by shell


# Nastavimo transakcijo
# And what this does is it means any command, it fails in the next command that we add to the script,
# it's going to fail the whole script
set -e

# Command for starting our service
python manage.py wait_for_db

# Well, this will do is it will collect all of the static files that I use for our project and it will
# put them in the configured static files directory.
# So when we start our application, we can make sure that all of the static files for all of the different
# apps in our project are copied to the same directory.
# So we can make that directory accessible by the engine x reverse proxy.
# That way we can serve all of the files directly from that directory instead of having to send them through
# the Django.
python manage.py collectstatic --noinput

# This is going to be used to run any migrations automatically whenever we start our app.
# So the database is migrated to the correct state when we start our app.
python manage.py migrate

# Run WSGI service
#
# We're passing in Socket 9000, which runs it on a TCP socket on Port 9000.
# And this point is going to be used from our nginx server to connect to our app.
#
# Application is going to be running on 4 workers
# (to število nastaviš glede na število CPU-jev, ki jih imaš na razpolago)
#
# master -->  which means you want to set the WSGI demon or the running application as
# the master thread. So, that's the main thing running on our server.
#
# enable-threads --> omogočimo multitasking
#
# module app.swgi --> povemo, da želimo zagnati ta modul (to je entry point to our project)
# Torej v naši aplikaciji: Recipe-app-api --> app --> app --> wsgi.py
# Ta file je narejen s strani Django.
#
# And because we're going to be running from the app directory in the Docker container, it's going to
# run app module.wsgipy and you don't need to specify the dot p y at the end because it will
# know to look for a python module by that name.
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi


