"""
Django settings for djaws project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REACT_APP =os.path.join(os.path.join(BASE_DIR, 'frontend'),)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY='6yl=")15olo_8dz1hplxo8*gxtj*t5!!lke6j58nl=s941n=c*%'
DEBUG = True
# SECURITY WARNING: don't run with debug turned on in production!

SITE_ID=2
#SITE_ID=2
ALLOWED_HOSTS = ["*"]

# Application definition
import datetime
INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # new
    'django_mysql',
    "django_extensions",
    'graphene_django',

    "items",
    "persons",
    "algorithm",
    "gql",

    'corsheaders',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ('*',)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'graphql_jwt.middleware.JSONWebTokenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
ROOT_URLCONF = 'djaws.urls'

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]
JWT_VERIFY_EXPIRATION=True
JWT_REFRESH_EXPIRATION_DELTA=70
JWT_EXPIRATION_DELTA=3600*70

GRAPHENE = {
    'SCHEMA': 'gql.schema.schema', # Where your Graphene schema lives
    'MIDDLEWARE': (
        'graphene_django.debug.DjangoDebugMiddleware',
    )
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'),),
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

WSGI_APPLICATION = 'djaws.wsgi.application'



# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

import os
if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            "HOST": "cbs-dra-03.ckdygqzbqwca.eu-west-2.rds.amazonaws.com",
            'NAME': 'dra',
            'USER': "canburaks",
            'PASSWORD':"06301987Cbs",
            'PORT': '3306',
        }
    }
CACHE_OPTIONS=[
    {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            "redis://cbs-redis-nocluster.drnxuo.0001.euw2.cache.amazonaws.com:6379/1",
        ],
        'OPTIONS': {

            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
},{
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        ################################################
        #choose your local redis port
        #"LOCATION": "redis://127.0.0.1:6379/1",
        "LOCATION": "127.0.0.1:6379",
        ################################################
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}]

CACHES = CACHE_OPTIONS[0] # 0=>Elasticache 1=>Local Redis

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_L10N = True

USE_TZ = True



WEBPACK_LOADER = {
    'DEFAULT': {
            'BUNDLE_DIR_NAME': '',
            'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
        }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL="https://s3.eu-west-2.amazonaws.com/cbs-static/static/"
MEDIA_URL="https://s3.eu-west-2.amazonaws.com/cbs-static/static/media/"

#STATIC_URL = '/static/'
STATIC_ROOT = 'static'
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]

MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media') #for upload files
LOGIN_REDIRECT_URL = "/"
"""
LOGIN_URL = "login"
LOGOUT_URL = "/"
LOGOUT_REDIRECT_URL = "home"
"""
