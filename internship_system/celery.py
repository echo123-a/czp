import os
from celery import Celery

# 设置 Django 项目的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internship_system.settings')

# 创建 Celery 应用实例
app = Celery('internship_system')

# 从 Django 设置中加载 Celery 配置，命名空间为 CELERY（即配置项以 CELERY_ 开头）
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有已注册 Django 应用中的 tasks.py 文件
app.autodiscover_tasks()