FROM nginx:alpine

# Install OpenSSL to generate certificates
RUN apk add --no-cache openssl

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the script to generate certificates
COPY generate_cert.sh /usr/local/bin/generate_cert.sh
RUN chmod +x /usr/local/bin/generate_cert.sh

# Set the entrypoint to run the script before starting Nginx
CMD ["/usr/local/bin/generate_cert.sh"]