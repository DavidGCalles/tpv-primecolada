#!/bin/sh

# If BACKEND_URL is set, use it. Otherwise, construct from host and port.
if [ -n "$BACKEND_URL" ]; then
  export PROXY_PASS_URL=$BACKEND_URL
else
  export PROXY_PASS_URL="http://${BACKEND_HOST:-localhost}:${BACKEND_PORT:-5000}"
fi

# Substitute environment variables in the nginx template
envsubst '${PORT} ${PROXY_PASS_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g 'daemon off;'
