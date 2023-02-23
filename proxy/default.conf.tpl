# Configuration block for the server.
# That's what the ngnix will look for in order to configure the server.
server {

    # The port that the server is going to listen on.
    # It a variable and value it going to be passed to our application.
    listen ${LISTEN_PORT};

    # Mapping
    #
    # So location blocks are ways that you can map different URL mappings for that passed into the Szabo requests
    # and you can map them to different places on the system.
    #
    # So any your row that starts with /static will go to an alias called /vol/static,
    # which has a volume containing the static and media files for our application.
    location /static {
        alias /vol/static;
    }

    # Then we have another location block for just forward slash.
    # And this basically handles the rest of the requests that aren't met by the above block.
    #
    # If it matches the forward slash static, then it will pass it to Alias and it will stop executing the
    # request if it doesn't match static.
    # Then it will just pass it to this second location block and map it to the server.
    location / {
         # And we're configuring the server by the app host and the app port.
        uwsgi_pass              ${APP_HOST}:${APP_PORT};

        # So WSGI params are parameters that are required for the HTTP request to be processed in uWSGI.
        # And we're going to be configuring our file next.
        # It's basically a list of different parameters that pass from the HTTP request to the running service.
        include                 /etc/nginx/uwsgi_params;

        # This is the maximum body size of the request that will be passed.
        # So it basically means here that the maximum image that can be uploaded will be ten megabytes.
        client_max_body_size    10M;
    }
}