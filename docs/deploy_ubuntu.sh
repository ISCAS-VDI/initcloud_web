# Author: Arthur.Yang
# Mail : yang_sirone@163.com

 -## 1. system reqiurements

    >cat /etc/lsb-release

    DISTRIB_ID=Ubuntu
    DISTRIB_RELEASE=14.04
    DISTRIB_CODENAME=trusty
    DISTRIB_DESCRIPTION="Ubuntu 14.04.3 LTS"

    >cat /etc/apt/source.list

    deb http://mirrors.aliyun.com/ubuntu/ trusty main multiverse restricted universe
    deb http://mirrors.aliyun.com/ubuntu/ trusty-backports main multiverse restricted universe
    deb http://mirrors.aliyun.com/ubuntu/ trusty-proposed main multiverse restricted universe
    deb http://mirrors.aliyun.com/ubuntu/ trusty-security main multiverse restricted universe
    deb http://mirrors.aliyun.com/ubuntu/ trusty-updates main multiverse restricted universe
    deb-src http://mirrors.aliyun.com/ubuntu/ trusty main multiverse restricted universe
    deb-src http://mirrors.aliyun.com/ubuntu/ trusty-backports main multiverse restricted universe
    deb-src http://mirrors.aliyun.com/ubuntu/ trusty-proposed main multiverse restricted universe
    deb-src http://mirrors.aliyun.com/ubuntu/ trusty-security main multiverse restricted universe
    deb-src http://mirrors.aliyun.com/ubuntu/ trusty-updates main multiverse restricted universe

    >apt-get update && apt-get upgrade


 -## 2. group and user

    >groupadd initcloud
    >useradd initcloud -g initcloud -m -d /opt/initcloud

    >cat /etc/sudoers.d/initcloud
    initcloud ALL=(ALL) NOPASSWD:ALL

    >mkdir -p /var/log/initcloud
    >chown -R initcloud:initcloud /var/log/initcloud

 -## 3. install system dependences

    >apt-get install python-pip apache2 mysql-client python-dev libffi-dev libssl-dev libmysqlclient-dev libapache2-mod-wsgi libldap2-dev libsasl2-dev

    # if is all in one environment
    >apt-get install mysql-server rabbitmq-server

 -## 4. pip virtualenv
 -
 -    >pip install virtualenv
 -
 -
 -## 5. config initcloud_web
 -    
 -    >cd /var/www/initcloud_web
 -    >virtualenv .venv
 -    >.venv/bin/pip install -r requirements.txt
 -
 -### 6. create db and user
 -
 -    # mysql -uroot
 -    >create database cloud_web CHARACTER SET utf8;
 -    >create user cloud_web;
 -    >grant all privileges on cloud_web.* to 'cloud_web'@'%' identified by 'password' with grant option;
 -    >flush privileges;
 -
 -### 7. generate local_settings.py
 -
 -    > cd /var/www/initcloud_web
 -    > .venv/bin/python initcloud_web/manage.py migrate_settings
 -
 -### 8. migrate db
 -    >cd /var/www/initcloud_web
 -    >.venv/bin/python initcloud_web/manage.py migrate
 -
 -
 -### 9. create super user
 -
 -    >cd /var/www/initcloud_web
 -    >.venv/bin/python initcloud_web/manage.py createsuperuser
 -
 -
 -### 10. init flavor
 -
 -
 -    >cd /var/www/initcloud_web
 -    >.venv/bin/python initcloud_web/manage.py init_flavor
 -
 -
 -### 11. test web 
 -
 -    >cd /var/www/initcloud_web
 -    >.venv/bin/python initcloud_web/manage.py runserver 0.0.0.0:8081
 -
 -

 -### 12. staff
      cd /var/www/initcloud_web
 -     .venv/bin/python initcloud_web/manage.py create_audit_user_permission
 -     .venv/bin/python initcloud_web/manage.py create_system_user_permission
 -     .venv/bin/python initcloud_web/manage.py create_safety_user_permission

 -    chmod 777 /etc/nova/policy.json
 -    chmod 777 /etc/cinder/policy.json
 -    chmod 777 /etc/neutron/policy.json

 -    source /root/keystone_admin
 -    openstack project create test

 -### 13. Celery worker
 -
 -    >rabbitmqctl add_user initcloud_web password
 -    >rabbitmqctl add_vhost initcloud
 -    >rabbitmqctl set_permissions -p initcloud initcloud_web ".*" ".*" ".*"
 -
 -    > cp docs/celery/celeryd.conf /etc/default/celeryd
 -    > cp docs/celery/celeryd /etc/init.d/celeryd
 -    > cp docs/celery/celerybeat /etc/init.d/celerybeat
 -
 -
 -    >chown -R initcloud:initcloud /var/log/initcloud/celery_task.log
 -    >chgrp -R initcloud /var/log/initcloud/celery_task.log
 -    >chown -R initcloud:initcloud /var/log/initcloud/initcloud.log
 -    >chgrp -R initcloud /var/log/initcloud/initcloud.log
 -    
 -    >chmod +x /etc/init.d/celeryd
 -    > /etc/init.d/celeryd restart
 -    > /etc/init.d/celeryd status
 -    >chmod +x /etc/init.d/celerybeat 
 -    > /etc/init.d/celerybeat restart
 -    > /etc/init.d/celerybeat status
 -### 14 run_celery with auto start
 -
      >vim /etc/rc.d/rc.local
      su - initcloud -c "cd /var/www/initcloud_web/initcloud_web/;../.venv/bin/celery multi restart initcloud_worker -A cloud --pidfile=/var/log/initcloud/celery_%n.pid --logfile=/var/log/initcloud/celery_%n.log &"
      > chmod +x /etc/rc.d/rc.local

  -## 15 deploy on apache (nginx in beta3)

      > add Listen port in apache
      > vim /etc/httpd/conf/ports.conf
        Listen 8081
      > copy 16-initcloud.conf to /etc/httpd/conf.d/
      > modify 16-initcloud.conf,like ServerName,ServerAlias
      > service apache2 restart

  -## 16 check

      > browser test.

  -## 17 reboot

  -## 18 trouble shooting

   
