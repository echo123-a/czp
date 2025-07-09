# users/admin.py
import logging
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import UserProfile, Student, Teacher
from django import forms
from django.contrib.auth.admin import UserAdmin

logger = logging.getLogger(__name__)


class StudentCreationForm(forms.ModelForm):
    """自动创建关联用户的表单"""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    class Meta:
        model = Student
        fields = ['student_id', 'class_group', 'major']

    def save(self, commit=True):
        # 创建用户
        user = UserProfile.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data.get('email', ''),
            is_teacher=False  # 明确学生身份
        )

        # 创建学生档案并关联用户
        student = super().save(commit=False)
        student.user = user

        if commit:
            student.save()
        return student


class TeacherCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    class Meta:
        model = Teacher
        fields = ['teacher_id', 'managed_classes']

    def save(self, commit=True):
        user = UserProfile.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data.get('email', ''),
            is_teacher=True  # 明确教师身份
        )

        teacher = super().save(commit=False)
        teacher.user = user

        if commit:
            teacher.save()
        return teacher


# 自定义UserAdmin类
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_teacher', 'display_groups')
    filter_horizontal = ('groups',)  # 只保留组

    # 自定义字段集
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email')}),
        ('角色信息', {'fields': ('is_teacher', 'groups')}),  # 只保留组选择
        ('状态', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )

    # 添加表单
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_teacher', 'groups'),
        }),
    )

    def display_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    display_groups.short_description = '所属组'

    # 完全移除权限字段
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields.pop('user_permissions', None)
        return form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 添加/移除Teachers组
        teachers_group, _ = Group.objects.get_or_create(name='Teachers')
        if obj.is_teacher:
            obj.groups.add(teachers_group)
            logger.info(f"用户 {obj.username} 添加到Teachers组")
        else:
            obj.groups.remove(teachers_group)
            logger.info(f"用户 {obj.username} 从Teachers组移除")

        # 确保权限正确
        from .models import assign_user_permissions
        assign_user_permissions(sender=UserProfile, instance=obj, created=False)


# 注册模型
admin.site.register(UserProfile, CustomUserAdmin)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentCreationForm
    list_display = ('user', 'student_id', 'class_group', 'major')
    """学生模型的管理类"""
    fields = ['username', 'password', 'email', 'student_id', 'class_group', 'major']
    list_filter = ('class_group', 'major')
    search_fields = ('user__username', 'student_id')

    def username(self, obj):
        return obj.user.username

    username.short_description = '用户名'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f"Student {obj.user.username} saved {'(updated)' if change else '(created)'}")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        logger.info(f"Student {obj.user.username} deleted")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """教师模型的管理类"""
    form = TeacherCreationForm
    list_display = ('username', 'teacher_id', 'managed_classes')
    fields = ['username', 'password', 'email', 'teacher_id', 'managed_classes']
    search_fields = ('user__username', 'teacher_id')

    def username(self, obj):
        return obj.user.username

    username.short_description = '用户名'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(f"Teacher {obj.user.username} saved {'(updated)' if change else '(created)'}")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        logger.info(f"Teacher {obj.user.username} deleted")