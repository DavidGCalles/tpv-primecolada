#!/bin/sh

# Set default values for environment variables if they are not already set
export BACKEND_HOST=${BACKEND_HOST:-backend}
export BACKEND_PORT=${BACKEND_PORT:-5000}

# Substitute environment variables in the nginx template
envsubst '${PORT} ${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g 'daemon off;'
