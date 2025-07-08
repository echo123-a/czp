import logging
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.urls import path
from django.core.cache import cache
from .models import Department, Class, SystemConfig, Notification, AuditLog
from .views import TeacherDashboardView
from django.contrib.auth.models import Group
from users.models import UserProfile

logger = logging.getLogger(__name__)

# 创建自定义AdminSite
class CustomAdminSite(admin.AdminSite):
    site_header = '实习周报管理系统'
    site_title = '实习周报管理'
    index_title = '系统管理'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(TeacherDashboardView.as_view()), name='teacher_dashboard')
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        # 在Admin首页添加仪表板链接
        extra_context = extra_context or {}
        extra_context['has_dashboard'] = True
        return super().index(request, extra_context=extra_context)

# 创建自定义AdminSite实例（必须在最顶部定义）
custom_admin_site = CustomAdminSite(name='custom_admin')

# 使用自定义AdminSite注册核心模型
@admin.register(Department, site=custom_admin_site)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_class_count')
    search_fields = ('name', 'code')
    list_per_page = 20

    def get_class_count(self, obj):
        cache_key = f'department_{obj.id}_class_count'
        count = cache.get(cache_key)
        if count is None:
            count = obj.class_set.count()
            cache.set(cache_key, count, 60 * 10)  # 缓存10分钟
        return count
    get_class_count.short_description = '班级数量'

@admin.register(Class, site=custom_admin_site)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'department', 'advisor', 'advisor_is_teacher')
    list_filter = ('department', 'year')
    search_fields = ('name', 'department__name', 'advisor__username')
    raw_id_fields = ('advisor',)
    list_select_related = ('department', 'advisor')
    list_per_page = 30

    def advisor_is_teacher(self, obj):
        return obj.advisor.is_teacher if obj.advisor else False
    advisor_is_teacher.short_description = '是否为教师'
    advisor_is_teacher.boolean = True

@admin.register(SystemConfig, site=custom_admin_site)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    fields = ('key', 'value', 'is_active')

@admin.register(Notification, site=custom_admin_site)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('recipients',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'content', 'notification_type')}),
        ('接收设置', {'fields': ('recipients', 'expire_at')}),
        ('状态', {'fields': ('is_read', 'created_at')}),
    )

@admin.register(AuditLog, site=custom_admin_site)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'description', 'object_id')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# 注册Django内置的LogEntry到自定义admin
custom_admin_site.register(LogEntry)

# 确保其他应用模型已注册
try:
    from reports.models import Report
    from reports.admin import ReportAdmin
    custom_admin_site.register(Report, ReportAdmin)
except ImportError as e:
    logger.error(f"Failed to register Report model: {e}")

try:
    from users.models import UserProfile, Student, Teacher
    from users.admin import CustomUserAdmin, StudentAdmin, TeacherAdmin
    custom_admin_site.register(UserProfile, CustomUserAdmin)
    custom_admin_site.register(Student, StudentAdmin)
    custom_admin_site.register(Teacher, TeacherAdmin)
except ImportError as e:
    logger.error(f"Failed to register UserProfile, Student, Teacher models: {e}")

# 注册Group模型
custom_admin_site.register(Group)