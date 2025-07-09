# core/models.py
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="院系名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="院系代码")

    class Meta:
        verbose_name = "院系"
        verbose_name_plural = "院系"
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "院系"
        verbose_name_plural = "院系"
        ordering = ['code']
        # 添加教师仪表板权限
        permissions = [
            ('view_teacher_dashboard', '可以查看教师仪表板'),
        ]


class Class(models.Model):
    name = models.CharField(max_length=50, verbose_name="班级名称")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属院系")
    year = models.PositiveSmallIntegerField(verbose_name="入学年份")
    # 修改为引用 settings.AUTH_USER_MODEL
    advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        # 优化筛选条件：同时匹配"Teachers组"或"is_teacher=True"
        limit_choices_to=Q(groups__name='Teachers') | Q(is_teacher=True),
        verbose_name="班主任"
    )

    class Meta:
        verbose_name = "班级"
        verbose_name_plural = "班级"
        unique_together = ('name', 'year')
        ordering = ['-year', 'name']

    def __str__(self):
        return f"{self.year}级{self.name}班"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('system', '系统通知'),
        ('alert', '紧急提醒'),
        ('reminder', '日程提醒'),
    )

    title = models.CharField(max_length=200, verbose_name="通知标题")
    content = models.TextField(verbose_name="通知内容")
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system',
        verbose_name="通知类型"
    )
    # 修改为引用 settings.AUTH_USER_MODEL
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="接收用户")
    is_read = models.BooleanField(default=False, verbose_name="已读状态")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    expire_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间")

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = "通知"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"

    def get_absolute_url(self):
        return reverse('core:notification_detail', kwargs={'pk': self.pk})


class AuditLog(models.Model):
    ACTION_TYPES = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('login', '登录'),
        ('logout', '登出'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name="操作类型")
    model_name = models.CharField(max_length=100, verbose_name="模型名称")
    object_id = models.CharField(max_length=100, verbose_name="对象ID")
    description = models.TextField(verbose_name="操作描述")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    user_agent = models.CharField(max_length=300, blank=True, verbose_name="用户代理")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        verbose_name = "审计日志"
        verbose_name_plural = "审计日志"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
        permissions = [
            ('can_view_auditlog', '可以查看审计日志'),
        ]

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.model_name} at {self.timestamp}"


# 新增 SystemConfig 类
class SystemConfig(models.Model):
    # 这里可以根据实际需求添加字段
    key = models.CharField(max_length=100, unique=True, verbose_name="配置键")
    value = models.TextField(verbose_name="配置值")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "系统配置"
        verbose_name_plural = "系统配置"

    def __str__(self):
        return f"{self.key}: {self.value}"

