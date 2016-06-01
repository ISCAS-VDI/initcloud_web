# !/bin/sh

# $1 could be makemigrations, startproject, startapp


/var/www/initcloud_web/.venv/bin/python /var/www/initcloud_web/initcloud_web/manage.py $1 $2
