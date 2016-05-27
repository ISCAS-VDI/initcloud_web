# !/bin/sh

echo "---------- add celery auto start ------------"
su - initcloud -c "cd /var/www/initcloud_web/initcloud_web/;../.venv/bin/celery multi restart initcloud_worker -A cloud --pidfile=/var/log/initcloud/celery_%n.pid --logfile=/var/log/initcloud/celery_%n.log &"
