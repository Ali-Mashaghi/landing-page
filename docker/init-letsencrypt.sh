#!/bin/sh
set -e

DOMAIN="${1:-mashaghi.ir}"
EMAIL="${2:-admin@mashaghi.ir}"
EXTRA_DOMAIN="${3:-www.mashaghi.ir}"

if ! command -v docker > /dev/null 2>&1; then
  echo "docker is required."
  exit 1
fi

echo "Starting nginx for certificate challenge..."
docker compose up -d nginx web db

echo "Requesting certificate for ${DOMAIN} and ${EXTRA_DOMAIN}..."
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN" \
  -d "$EXTRA_DOMAIN"

echo "Switching nginx to SSL config..."
cp docker/nginx/ssl.conf docker/nginx/default.conf
docker compose restart nginx

echo "SSL setup complete. Site should be available at https://${DOMAIN}"
