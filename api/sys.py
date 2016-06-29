# encoding: utf-8
import os
from django.conf import settings

#apache服务
# 1.重启
# 2.关闭
def apache(status=1):
    path = settings.BASE_DIR+'/api/flow/apache_server.sh'
    return os.system('bash '+path)
