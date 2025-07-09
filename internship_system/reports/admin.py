import logging
from django.contrib import admin
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Report
from import_export import resources
from import_export.admin import ImportExportModelAdmin

logger = logging.getLogger(__name__)

class ReportResource(resources.ModelResource):
    class Meta:
        model = Report
        fields = ('id', 'student__username', 'week', 'company', 'position',
                  'status', 'is_urgent', 'created_at')
        export_order = fields

class ReportAdmin(ImportExportModelAdmin):
    resource_class = ReportResource
    list_display = ('student', 'week', 'company', 'status', 'is_urgent', 'created_at')
    list_filter = ('status', 'week', 'is_urgent')
    search_fields = ('student__username', 'company', 'position')
    list_editable = ('is_urgent',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('student', 'week', 'company', 'position', 'status')
        }),
        ('内容', {
            'fields': ('content', 'problems', 'feedback')
        }),
        ('状态', {
            'fields': ('is_urgent',)
        }),
        ('时间', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_urgent', 'mark_as_normal']

    def mark_as_urgent(self, request, queryset):
        for report in queryset:
            report.is_urgent = True
            report.save()
        logger.info(f"{queryset.count()} reports marked as urgent")

    mark_as_urgent.short_description = "标记为紧急"

    def mark_as_normal(self, request, queryset):
        for report in queryset:
            report.is_urgent = False
            report.save()
        logger.info(f"{queryset.count()} reports marked as normal")

    mark_as_normal.short_description = "标记为正常"

admin.site.register(Report, ReportAdmin)

@receiver(pre_save, sender=Report)
def pre_save_report(sender, instance, **kwargs):
    # 可以在这里添加更多的处理逻辑
    pass