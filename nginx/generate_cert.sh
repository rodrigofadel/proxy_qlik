#!/bin/sh

CERT_DIR="/etc/nginx/certificates"
CERT_KEY="$CERT_DIR/nginx-selfsigned.key"
CERT_CRT="$CERT_DIR/nginx-selfsigned.crt"

# If the certificates do not already exist, create a new self-signed certificate
if [ ! -f "$CERT_KEY" ] || [ ! -f "$CERT_CRT" ]; then
    echo "🔹 Generating self-signed SSL certificate..."
    mkdir -p "$CERT_DIR"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERT_KEY" \
        -out "$CERT_CRT" \
        -subj "/C=BR/ST=SP/L=Localhost/O=Dev/OU=IT/CN=localhost"
else
    echo "✅ SSL certificate already exists. Skipping generation..."
fi

# Start Nginx
echo "🚀 Starting Nginx..."
exec nginx -g "daemon off;"
