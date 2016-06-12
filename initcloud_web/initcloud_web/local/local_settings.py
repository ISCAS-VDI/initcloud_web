#-*- coding=utf-8 -*-
from datetime import timedelta
import ldap
from django_auth_ldap.config import LDAPSearch

#### site config

BRAND = u"openstack"
EMAIL_SUBJECT_PREFIX = u"[%s]" % BRAND
ICP_NUMBER = u"京- default"
COPY_RIGHT = u"2015 © default"
DNS_NAMESERVERS = ["8.8.4.4", "114.114.114.114"]
THEME_NAME = 'blue'
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
TRI_ENABLED = True
CAPTCHA_ENABLED = False
REGISTER_ENABLED = True 
REGISTER_ACTIVATE_EMAIL_ENABLED = False
DEFAULT_ROUTER_AUTO_SET_GATEWAY = True
ACTIVATE_EMAIL_EXPIRE_DAYS = timedelta(30)

#### mail
ADMINS = (("15210121696@163.com"), )
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
OS_NAME_PREFIX = u"initcloud"


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
