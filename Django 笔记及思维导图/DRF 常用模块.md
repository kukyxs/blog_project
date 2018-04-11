##### DRF 常用模块

```python
from django.contrib.auth.models import User # 用户模型
from django_filters.rest_framework import DjangoFilterBackend  # 多条件筛选类
from rest_framework import permissions  # 权限设置类
from rest_framework import status  # 返回状态值
from rest_framework import viewsets  # 视图
from rest_framework.authentication import TokenAuthentication  # 认证类
from rest_framework.authtoken.models import Token  # token 模型
from rest_framework.authtoken.views import ObtainAuthToken  # 获取 token 视图
from rest_framework.response import Response  # 视图返回的相应
from rest_framework.views import APIView  # 视图


import django_filters  # 自定义多条件筛选类时候需要用到


import rest_framework.pagination  # 自定义分页需要用到


from rest_framework import permissions  # 自定义权限类需要用到


from rest_framework import serializers  # 定义序列化类需要用到


from django.conf.urls import url  # 绑定 url 时候用到
from rest_framework import routers  # 注册路由
from rest_framework.urlpatterns import format_suffix_patterns  # 解析网址格式用到


# 创建用户同时创建 token 值 需要用到
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)
```

