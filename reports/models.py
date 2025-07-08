from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone

from django.conf import settings


class Report(models.Model):
    """实习报告模型"""
    STATUS_CHOICES = [
        ('job', '求职中'),
        ('intern', '实习中'),
        ('signed', '已签约'),
        ('other', '其他'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    week = models.IntegerField(verbose_name="周次", choices=[(i, f"第{i}周") for i in range(1, 53)])
    company = models.CharField(max_length=100, blank=True, verbose_name="实习单位")
    position = models.CharField(max_length=100, blank=True, verbose_name="岗位")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='intern',
        verbose_name="就业状态"
    )
    content = models.TextField(verbose_name="实习内容与进展")
    problems = models.TextField(verbose_name="遇到的问题", blank=True)
    feedback = models.TextField(verbose_name="教师反馈", blank=True)
    is_urgent = models.BooleanField(default=False, verbose_name="需紧急关注")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        permissions = [
            ("can_view_all_reports", "可以查看所有报告"),      # 教师权限
            ("can_change_any_report", "可以修改任何报告"),    # 教师权限
            ("can_view_own_report", "可以查看自己的报告"),    # 学生权限
            ("can_create_report", "可以创建报告"),           # 学生权限
        ]
    def __str__(self):
        return f"{self.student.username} - 第{self.week}周报告"


class CustomUser(AbstractUser):
    # 添加 related_name 参数以避免冲突
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='reports_customuser_groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='reports_customuser_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class ReportComment(models.Model):
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='report_comments'  # 修改 related_name 以避免冲突
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='report_comments_user'  # 为避免冲突，添加一个不同的 related_name
    )
    content = models.TextField(verbose_name="评论内容")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="提交时间")

    class Meta:
        verbose_name = "报告评论"
        verbose_name_plural = "报告评论"
        ordering = ['-created_at']  # 按时间倒序排列

    def __str__(self):
        return f"{self.user.username} 对 {self.report} 的评论"