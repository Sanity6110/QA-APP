#!/usr/bin/env bash
set -euo pipefail

# install_phpmyadmin.sh
# Installs phpMyAdmin on Ubuntu+Apache+MySQL,
# deploys it to /var/www/html/, and configures Apache.

# 0) Ensure we're root
if [[ $EUID -ne 0 ]]; then
  echo "Please run as root: sudo $0"
  exit 1
fi

# 1) Grab MySQL root password from env
: "${MYSQL_ROOT_PW:?ERROR: set MYSQL_ROOT_PW environment variable before running}"
export DEBIAN_FRONTEND=noninteractive

echo "● Enabling universe repo…"
apt-get update -qq
if ! grep -q '^deb .\+ universe' /etc/apt/sources.list /etc/apt/sources.list.d/*; then
  apt-get install -y software-properties-common >/dev/null
  add-apt-repository universe -y >/dev/null
  apt-get update -qq
fi

echo "● Pre-seeding phpMyAdmin…"
debconf-set-selections <<EOF
phpmyadmin phpmyadmin/dbconfig-install boolean true
phpmyadmin phpmyadmin/app-password-confirm password $MYSQL_ROOT_PW
phpmyadmin phpmyadmin/mysql/admin-pass password $MYSQL_ROOT_PW
phpmyadmin phpmyadmin/mysql/app-pass password $MYSQL_ROOT_PW
phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2
EOF

echo "● Installing phpMyAdmin + PHP extensions…"
apt-get install -y phpmyadmin php-mbstring php-zip php-gd php-json php-curl >/dev/null

echo "● Enabling PHP modules…"
phpenmod mbstring zip >/dev/null

echo "● Clearing default site…"
rm -rf /var/www/html/*

echo "● Deploying phpMyAdmin into /var/www/html…"
cp -R /usr/share/phpmyadmin/* /var/www/html/
chown -R www-data:www-data /var/www/html

echo "● Writing Apache conf for phpMyAdmin alias…"
cat >/etc/apache2/conf-available/phpmyadmin.conf <<'CONF'
Alias /phpmyadmin /usr/share/phpmyadmin
<Directory /usr/share/phpmyadmin>
    Options Indexes FollowSymLinks
    DirectoryIndex index.php
    Require all granted
</Directory>
CONF

echo "● Enabling phpMyAdmin conf…"
a2enconf phpmyadmin >/dev/null

echo "● Reloading Apache…"
systemctl reload apache2

echo
echo "✅ phpMyAdmin is now available:"
echo "   • At http://<your-server-ip>/   (your default site)"
echo "   • Also at http://<your-server-ip>/phpmyadmin"
echo
echo "   Log in with MySQL root / the password in \$MYSQL_ROOT_PW"
 