#!/bin/sh

cd /var/www/initcloud_web/initcloud_web/
../.venv/bin/celery multi stop initcloud_worker --pidfile=/var/log/initcloud/celery_%n.pid


/etc/init.d/celeryd stop
/etc/init.d/celerybeat stop
ps -ef | grep celery
