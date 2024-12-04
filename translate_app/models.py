from django.db import models
from django.contrib.auth.models import User

# 注册密钥表
class RegistrationKey(models.Model):
    key = models.CharField(max_length=512, unique=True, verbose_name='注册密钥')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')

    def __str__(self):
        return self.key


# 用户信息表
class Info(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='info', verbose_name='用户信息')
    registration_key = models.ForeignKey(
        RegistrationKey, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='注册密钥'
    )

    def __str__(self):
        return f"{self.user.username} 的信息"


# 评分记录表
class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translations', verbose_name='用户')
    original_text = models.TextField(verbose_name='原文')
    translated_text = models.TextField(verbose_name='译文')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='评分')
    review = models.TextField(verbose_name='评价')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    year = models.IntegerField(verbose_name='年份')

    def __str__(self):
        return f"{self.user.username} - {self.upload_time} - {self.score}"
