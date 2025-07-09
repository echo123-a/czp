# users/models.py
import logging

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from guardian.shortcuts import assign_perm

logger = logging.getLogger(__name__)

class UserProfile(AbstractUser):
    """自定义用户模型"""
    is_teacher = models.BooleanField(default=False, verbose_name=_("是否教师"))

    # 必填字段（当使用createsuperuser命令时需要的字段，不包括USERNAME_FIELD和password）
    REQUIRED_FIELDS = ['email']  # 示例：要求邮箱必填

    # 作为唯一标识的字段（通常是username或email）
    USERNAME_FIELD = 'username'

    # 自定义管理器
    objects = UserManager()

    class Meta:
        verbose_name = _("用户")
        verbose_name_plural = _("用户")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def student_profile(self):
        try:
            return self.student
        except Student.DoesNotExist:
            return None

class Student(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True, verbose_name=_("学号"))
    class_group = models.CharField(max_length=50, verbose_name=_("班级"))
    major = models.CharField(max_length=50, verbose_name=_("专业"))

class Teacher(models.Model):
    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='teacher_profile'
    )
    teacher_id = models.CharField(max_length=20, unique=True, verbose_name=_("教师工号"))
    managed_classes = models.CharField(
        max_length=255,
        help_text=_("管理的班级，用逗号分隔"),
        verbose_name=_("管理班级")
    )


@receiver(post_save, sender=UserProfile)
def assign_user_permissions(sender, instance, created, **kwargs):
    if created:
        try:
            # 获取或创建组
            student_group, _ = Group.objects.get_or_create(name='Students')
            teacher_group, _ = Group.objects.get_or_create(name='Teachers')

            # 获取权限
            perms = {
                'create': Permission.objects.get(codename='can_create_report'),
                'view_own': Permission.objects.get(codename='can_view_own_report'),
                'view_all': Permission.objects.get(codename='can_view_all_reports'),
                'change_all': Permission.objects.get(codename='can_change_any_report'),
            }

            if instance.is_teacher:
                # 添加到教师组并分配权限
                instance.groups.add(teacher_group)
                teacher_group.permissions.add(perms['view_all'], perms['change_all'])
                logger.info(f"教师 {instance.username} 已添加到Teachers组并分配权限")
            else:
                # 添加到学生组并分配权限
                instance.groups.add(student_group)
                student_group.permissions.add(perms['create'], perms['view_own'])
                logger.info(f"学生 {instance.username} 已添加到Students组并分配权限")

        except Exception as e:
            logger.error(f"用户组/权限分配出错: {e}")


@receiver(post_save, sender=UserProfile)
def create_user_profile(sender, instance, created, **kwargs):
    """自动创建对应的学生/教师档案"""
    if created:
        try:
            if instance.is_teacher:
                Teacher.objects.get_or_create(user=instance)
            else:
                Student.objects.get_or_create(user=instance)
        except Exception as e:
            logger.error(f"创建用户档案失败: {e}")


@receiver(post_save, sender=Student)
@receiver(post_save, sender=Teacher)
def update_user_role(sender, instance, created, **kwargs):
    """确保档案与用户角色一致"""
    try:
        if isinstance(instance, Student):
            instance.user.is_teacher = False
        elif isinstance(instance, Teacher):
            instance.user.is_teacher = True

        instance.user.save()
    except Exception as e:
        logger.error(f"更新用户角色失败: {e}")