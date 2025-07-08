from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import AuditLog

User = get_user_model()

@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    if sender._meta.app_label == 'core' and sender.__name__ != 'AuditLog':
        action = 'create' if created else 'update'
        description = f"{instance} 被{'创建' if created else '更新'}"
        AuditLog.objects.create(
            user=getattr(instance, 'last_modified_by', None),
            action=action,
            model_name=f"{sender._meta.app_label}.{sender.__name__}",
            object_id=str(instance.pk),
            description=description
        )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender._meta.app_label == 'core' and sender.__name__ != 'AuditLog':
        AuditLog.objects.create(
            user=getattr(instance, 'last_modified_by', None),
            action='delete',
            model_name=f"{sender._meta.app_label}.{sender.__name__}",
            object_id=str(instance.pk),
            description=f"{instance} 被删除"
        )