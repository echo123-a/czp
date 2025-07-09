from .base import *  # 导入基础配置
import os
import dj_database_url

# 安全设置
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,172.24.52.87').split(',')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# 数据库配置
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# 静态文件
STATIC_ROOT = '/app/staticfiles'
STATIC_URL = '/static/'

# 媒体文件
MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'

# HTTPS 安全设置
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Celery 配置
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL')