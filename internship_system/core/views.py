# core/views.py
from django.contrib.auth.views import LoginView
from django.db.models import Count, Max, Q
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Department, Class, Notification, AuditLog
from reports.models import Report
import logging
from django.urls import reverse
logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'system_name': '实习管理系统',
            'welcome_text': '高效管理学生实习过程，实时跟踪实习状态，生成实习报告'
        })
        return context
    def form_valid(self, form):
        """确保登录时清除任何切换状态"""
        if 'original_user_id' in self.request.session:
            del self.request.session['original_user_id']
        return super().form_valid(form)


class TeacherDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'admin/teacher_dashboard.html'
    permission_required = 'core.view_teacher_dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # 获取基础数据
            total_reports = Report.objects.count()
            urgent_reports = Report.objects.filter(is_urgent=True).count()

            # 修复1：确保状态统计数据有效
            status_stats = []
            status_data = (
                Report.objects
                .values('status')
                .annotate(count=Count('id'))
                .order_by('status')
            )

            if status_data:
                total_count = sum(item['count'] for item in status_data)
                for item in status_data:
                    status_display = dict(Report.STATUS_CHOICES).get(
                        item['status'], f"未知状态 ({item['status']})"
                    )
                    percent = (item['count'] / total_count * 100) if total_count > 0 else 0
                    status_stats.append({
                        'status': item['status'],
                        'status_display': status_display,
                        'count': item['count'],
                        'percent': round(percent, 1)
                    })

            # 修复2：确保学生统计数据有效
            student_stats = (
                Report.objects
                .values('student__id', 'student__username')
                .annotate(
                    count=Count('id'),
                    urgent=Count('id', filter=Q(is_urgent=True)),
                    latest=Max('created_at')
                )
                .order_by('student__username')
            )

            # 获取最近报告
            reports = Report.objects.select_related('student').order_by('-created_at')[:10]

        except Exception as e:
            logger.exception(f"仪表板数据加载失败: {str(e)}")
            total_reports = 0
            urgent_reports = 0
            status_stats = []
            student_stats = []
            reports = []

        context.update({
            'total_reports': total_reports,
            'urgent_reports': urgent_reports,
            'status_stats': status_stats,
            'student_stats': student_stats,
            'reports': reports,
            # 添加调试标志
            # 'debug_mode': settings.DEBUG,
        })
        return context


# 以下其他视图保持不变...
class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'core/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20

    def get_queryset(self):
        return Department.objects.all().order_by('code')


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'core/department_detail.html'
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = self.object.class_set.all()
        return context


class ClassListView(LoginRequiredMixin, ListView):
    model = Class
    template_name = 'core/class_list.html'
    context_object_name = 'classes'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.GET.get('year')
        if year:
            queryset = queryset.filter(year=year)
        return queryset.select_related('department', 'advisor')


class ClassDetailView(LoginRequiredMixin, DetailView):
    model = Class
    template_name = 'core/class_detail.html'
    context_object_name = 'class_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = self.object.student_set.select_related('user')
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'core/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 15

    def get_queryset(self):
        return super().get_queryset().filter(recipients=self.request.user)


class NotificationDetailView(LoginRequiredMixin, DetailView):
    model = Notification
    template_name = 'core/notification_detail.html'
    context_object_name = 'notification'

    def get_queryset(self):
        return super().get_queryset().filter(recipients=self.request.user)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save()
        return response


class AuditLogListView(PermissionRequiredMixin, ListView):
    model = AuditLog
    template_name = 'core/audit_log_list.html'
    context_object_name = 'audit_logs'
    paginate_by = 50
    permission_required = 'core.view_auditlog'

    def get_queryset(self):
        return super().get_queryset().select_related('user').order_by('-timestamp')