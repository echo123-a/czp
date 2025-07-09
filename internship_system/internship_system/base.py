"""
Django settings for internship_system project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-c+^2o!cel+xk559w%0)^c(n)*pzekmw$d--7a=dqp-#&e@xyzo'
DEBUG = True
ALLOWED_HOSTS = []

# 自定义用户模型
AUTH_USER_MODEL = 'users.UserProfile'
ANONYMOUS_USER_NAME = 'AnonymousUser'

# 认证后端设置
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.backends.RoleBackend',  # 自定义角色认证
    'guardian.backends.ObjectPermissionBackend'  # 添加 Guardian 认证后端
]

# 登录/登出设置
LOGIN_URL = 'login'  # 指定登录页面URL
LOGIN_REDIRECT_URL = '/api/v1/reports/'
LOGOUT_REDIRECT_URL = 'login'  # 登出后重定向到登录页面

# 媒体文件设置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Crispy表单设置
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# 应用列表
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 自定义应用
    'core',
    'reports',
    'users',

    # 第三方应用
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'guardian',
    'import_export',
    'crispy_forms',
    'crispy_bootstrap5',
]

# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# URL配置
ROOT_URLCONF = 'internship_system.urls'

# 模板设置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # 项目级模板目录
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

# WSGI应用
WSGI_APPLICATION = 'internship_system.wsgi.application'

# 数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'  # 改为中国时区
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # 静态文件目录
STATIC_ROOT = BASE_DIR / 'staticfiles'  # 添加静态文件收集目录

# 默认主键字段
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allauth设置
ACCOUNT_EMAIL_VERIFICATION = 'none'  # 禁用邮箱验证
ACCOUNT_LOGIN_METHODS = {'username'}  # 使用用户名登录
ACCOUNT_LOGOUT_ON_GET = True  # GET请求直接登出

# Redis 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Celery 定时任务配置
CELERY_BEAT_SCHEDULE = {
    'send_reminders': {
        'task': 'reports.tasks.send_reminders',
        'schedule': 60 * 60 * 24,  # 每天执行一次
    },
}

# 任务序列化方式
CELERY_TASK_SERIALIZER = 'json'
# 结果序列化方式
CELERY_RESULT_SERIALIZER = 'json'
# 接受的内容类型
CELERY_ACCEPT_CONTENT = ['json']
# 时区（与 Django 时区保持一致）
CELERY_TIMEZONE = 'Asia/Shanghai'
# 是否启用 UTC
CELERY_ENABLE_UTC = False


# 缺少以下配置：
SESSION_COOKIE_SECURE = True  # 如果是HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2周，以秒为单位