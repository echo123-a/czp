from django.db import migrations


def create_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # 创建组
    student_group, _ = Group.objects.get_or_create(name='Students')
    teacher_group, _ = Group.objects.get_or_create(name='Teachers')

    # 获取权限
    perms = {
        'create': Permission.objects.get(codename='can_create_report'),
        'view_own': Permission.objects.get(codename='can_view_own_report'),
        'view_all': Permission.objects.get(codename='can_view_all_reports'),
        'change_all': Permission.objects.get(codename='can_change_any_report'),
    }

    # 分配权限到组
    student_group.permissions.add(perms['create'], perms['view_own'])
    teacher_group.permissions.add(perms['view_all'], perms['change_all'])


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # 替换为实际的上一迁移
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions),
    ]