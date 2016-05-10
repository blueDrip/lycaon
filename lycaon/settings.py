
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r1-#py2)14i*82ae55w14n-4s##%lb(+l=5ffpyrk12agyae*%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost','192.168.1.19']

LOG_DIR = '/home/sw/logs/lycaon/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lycaon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lycaon.wsgi.application'


P_NOUN_FILE=BASE_DIR +"/rules/conf/parent_noun_new.txt"
P_ADJ_FILE=BASE_DIR +"/rules/conf/parent_adj_new.txt"
P_NOUN_FILE_CH=BASE_DIR +"/rules/conf/parent_noun_ch_new.txt"
LOVER_NOUN_FILE=BASE_DIR +"/rules/conf/lover_noun_new.txt"
LOVER_ADJ_FILE=BASE_DIR +"/rules/conf/lover_adj_new.txt"
P_PARENT_DICT_NEW_CONF=BASE_DIR +"/rules/conf/parents_new.dict"


ID_FILE = BASE_DIR +"/data/id.txt"
TEL_NUM_FILE = BASE_DIR +"/data/tel_num.txt"
PHONE_FILE = BASE_DIR +"/data/phone.txt"

SMS_BAD_WORD_FILE= BASE_DIR + "/rules/conf/sms_badword.txt"
SENSE_BAD_WORD_FILE= BASE_DIR + "/rules/conf/sense_word.txt"
# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test',
        'USER': 'root',
        'PASSWORD': 'root',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}



# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

from logging.handlers import SysLogHandler

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(levelname)s\t%(asctime)s\t%(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'api': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + 'api.log',
            'formatter': 'standard',
        },
        'syslog': {
            'level': 'DEBUG',
            'address': '/dev/log',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'standard',
            'facility':'local0',
        },
        'others': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + 'others.log',
            'formatter': 'standard',
        },
        'rules': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + 'rules.log',
            'formatter': 'standard',
        },
        'sms': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + 'sms.log',
            'formatter': 'standard',
        },
        
    },
    'loggers': {
        'django.api':{
            'handlers': ['api'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.others': {
            'handlers': ['others'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.rules': {
            'handlers': ['rules'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.sms': {
            'handlers': ['sms'],
            'level': 'INFO',
            'propagate': True,
        },

    }
}

# from mongoengine import DEFAULT_CONNECTION_NAME
from mongoengine import  connect
connect('api_plus_plus',host='182.92.71.136',username='test',password='test')
