#!/bin/sh
set -e

DOMAIN="${1:-mashaghi.ir}"
EMAIL="${2:-aliu.mashaghi@gmail.com}"
WWW_DOMAIN="${3:-www.mashaghi.ir}"
RSA_KEY_SIZE=4096

if ! command -v docker > /dev/null 2>&1; then
  echo "docker is required."
  exit 1
fi

echo "==> Ensuring stack is up (HTTP)..."
docker compose up -d db web nginx

echo "==> Creating temporary self-signed cert so nginx can load SSL config..."
docker compose run --rm --entrypoint sh certbot -c "\
  mkdir -p /etc/letsencrypt/live/${DOMAIN} && \
  openssl req -x509 -nodes -newkey rsa:${RSA_KEY_SIZE} -days 1 \
    -keyout /etc/letsencrypt/live/${DOMAIN}/privkey.pem \
    -out /etc/letsencrypt/live/${DOMAIN}/fullchain.pem \
    -subj '/CN=${DOMAIN}'"

echo "==> Switching nginx to SSL config..."
cp docker/nginx/ssl.conf docker/nginx/default.conf
docker compose restart nginx

echo "==> Waiting for nginx..."
sleep 3

echo "==> Requesting Let's Encrypt certificate for ${DOMAIN} + ${WWW_DOMAIN}..."
docker compose run --rm --entrypoint sh certbot -c "\
  rm -rf /etc/letsencrypt/live/${DOMAIN} \
         /etc/letsencrypt/archive/${DOMAIN} \
         /etc/letsencrypt/renewal/${DOMAIN}.conf && \
  certbot certonly --webroot -w /var/www/certbot \
    --email ${EMAIL} \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d ${DOMAIN} \
    -d ${WWW_DOMAIN}"

echo "==> Reloading nginx with real certificate..."
docker compose exec nginx nginx -s reload

echo ""
echo "Done. Site: https://${DOMAIN}"
echo "Renewal: certbot service renews every 12 hours automatically."
