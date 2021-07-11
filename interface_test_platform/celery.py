from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interface_test_platform.settings')  # 设置django环境


app = Celery('interface_test_platform',backend='redis://127.0.0.1:6379/1', broker='redis://127.0.0.1:6379/0')

app.config_from_object('django.conf:settings') #  使用CELERY_ 作为前缀，在settings中写配置

app.autodiscover_tasks(lambda : settings.INSTALLED_APPS)  # 发现任务文件每个app下的task.py

# 时区
app.conf.timezone = 'Asia/Shanghai'
# 是否使用UTC
app.conf.enable_utc = False
