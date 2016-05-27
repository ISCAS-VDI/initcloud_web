#-*- coding=utf-8 -*-
from datetime import timedelta
import ldap
from django_auth_ldap.config import LDAPSearch

#### site config

BRAND = u"软件所openstack"
EMAIL_SUBJECT_PREFIX = u"[%s]" % BRAND
ICP_NUMBER = u"京- default"
COPY_RIGHT = u"2015 © default"
DNS_NAMESERVERS = ["8.8.4.4", "114.114.114.114"]
THEME_NAME = 'darkblue'
EXTERNAL_URL = 'http://127.0.0.1:8000/'
BATCH_INSTANCE = 10
DEFAULT_BANDWIDTH = 5
SEND_MAIL_WHEN_BACKEND_ERROR = False

OPENSTACK_SSL_NO_VERIFY = True
# OPENSTACK_SSL_CACERT = '/path/to/cacert.pem'

#### task config

INSTANCE_SYNC_INTERVAL_SECOND = 5
MAX_COUNT_SYNC = 60

#### function enable/disable

QUOTA_CHECK = True
MULTI_ROUTER_ENABLED = False
WORKFLOW_ENABLED = False
CAPTCHA_ENABLED = False
REGISTER_ENABLED = True
REGISTER_ACTIVATE_EMAIL_ENABLED = False
DEFAULT_ROUTER_AUTO_SET_GATEWAY = True
ACTIVATE_EMAIL_EXPIRE_DAYS = timedelta(30)

#### mail
ADMINS = (("1521012@163.com"), )
EMAIL_HOST = "smtp.163.com"
EMAIL_PORT = "25"
EMAIL_HOST_USER = "15210121696@163.com"
EMAIL_HOST_PASSWORD = "xnz0916"
DEFAULT_FROM_EMAIL = "15210121696@163.com"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

####

QUOTA_ITEMS = {
    "instance": 0,
    "vcpu": 0,
    "memory": 0,
    "floating_ip": 0,
    "volume": 0,
    "volume_size": 0,
}

DEFAULT_NETWORK_NAME = u"默认网络"
DEFAULT_SUBNET_NAME = u"默认子网"
DEFAULT_ROUTER_NAME = u"默认路由"
DEFAULT_FIREWALL_NAME = u"默认防火墙"
OS_NAME_PREFIX = u"ever"

#### backup configuration

RBD_COMPUTE_POOL = "compute"
RBD_VOLUME_POOL = "volumes"
BACKUP_RBD_HOST = "root@14.14.15.4:22"
BACKUP_RBD_HOST_PWD = "r00tme"
BACKUP_COMMAND_ARGS = {
    "source_pool": None,
    "image": None,
    "mode": None,
    "rbd_image": None,
    "dest_pool": "rbd",
    "dest_user": "root",
    "dest_host": "node-7",
}

BACKUP_ENABLED = True
BACKUP_CONNECTION_TIMEOUT = 200
BACKUP_QUERY_INTERVAL = timedelta(seconds=60)
BACKUP_QUERY_MAX_DURATION = timedelta(hours=12)

BACKUP_COMMAND = "python /opt/eontools/rbd_backup.py  -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o backup -m %(mode)s -a"
BACKUP_QUERY_COMMAND = "python /opt/eontools/rbd_backup.py  -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o query_backup -s %(rbd_image)s"
BACKUP_RESTORE_COMMAND = "python /opt/eontools/rbd_backup.py -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o restore -s %(rbd_image)s -a"
BACKUP_RESTORE_QUERY_COMMAND = "python /opt/eontools/rbd_backup.py -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o query_restore -s %(rbd_image)s"
BACKUP_DELETE_COMMAND = "python /opt/eontools/rbd_backup.py -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o delete -s %(rbd_image)s"
BACKUP_DU_COMMAND = "python /opt/eontools/rbd_backup.py -p %(source_pool)s -i %(image)s -r %(dest_pool)s -u %(dest_user)s -d %(dest_host)s -o du_snap -s %(rbd_image)s"

#### monitor configuration

MONITOR_ENABLED = True
MONITOR_CONFIG = {
    "enabled": MONITOR_ENABLED,
    "base_url": "http://127.0.0.1:5601",
    'monitors': [
        {
            "title": u"CPU",
            "url": "/#/visualize/edit/cpu?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:!'{[{uuid}]}!'')),vis:(aggs:!((id:'1',params:(field:cpu_util),schema:metric,type:avg),(id:'2',params:(extended_bounds:(),field:'@timestamp',interval:{[{ interval }]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!f,addTooltip:!f,defaultYExtents:!f,shareYAxis:!t),type:line))"
        },
        {
            "title": u"磁盘",
            "url": "#/visualize/edit/disk?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:{[{uuid}]}')),vis:(aggs:!((id:'1',params:(field:disk.read.bytes),schema:metric,type:avg),(id:'2',params:(field:disk.write.bytes),schema:metric,type:avg),(id:'3',params:(extended_bounds:(),field:'@timestamp',interval:{[{interval}]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTooltip:!t,defaultYExtents:!f,shareYAxis:!t),type:line))"
        },
        {
            "title": u"网络",
            "url": "#/visualize/edit/network?embed&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'resource_id:{[{uuid}]}')),vis:(aggs:!((id:'1',params:(field:network.incoming.bytes.rate),schema:metric,type:avg),(id:'2',params:(field:network.outgoing.bytes.rate),schema:metric,type:avg),(id:'3',params:(extended_bounds:(),field:'@timestamp',interval:{[{interval}]},min_doc_count:1),schema:segment,type:date_histogram)),listeners:(),params:(addLegend:!t,addTooltip:!t,defaultYExtents:!f,shareYAxis:!t),type:line))"
        }
    ],
    'intervals': ['second', 'minute', 'hour', 'day', 'week', 'month']
}

#### db & broker

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "cloud_web",
        'USER': "cloud_web",
        'PASSWORD': "password",
        'HOST': "127.0.0.1",
        'PORT': "3306",
        'TEST_CHARSET': 'utf8',
        'OPTIONS': {
            'init_command': 'SET storage_engine=INNODB',
        }
    }
}
CELERYD_HIJACK_ROOT_LOGGER = False
BROKER_URL = "amqp://initcloud_web:password@127.0.0.1:5672/initcloud"

# LDAP
LDAP_AUTH_ENABLED = False
