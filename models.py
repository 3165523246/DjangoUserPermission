from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


#用户表 (  包括  商家  用户  平台  ) #只是未来实现 而实现
# 通过对其 进行 分组和修改权限的操作     使其区分 身份
class User(AbstractUser):
    #继承内置User表
    choice_identity=(
        (1, '用户'),
        (2, '商家'),
        (3, '客服'),
    )
    #这里为 User内置 表添加啦字段
    flag=models.CharField(choices=choice_identity,default=1,max_length=20)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')


    class Meta:
        db_table='df_user'

class  Message(models.Model):
    context=models.CharField(max_length=255,verbose_name='内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')


