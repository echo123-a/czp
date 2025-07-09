# reports/views.py
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import permission_required, user_passes_test
import csv
from django_comments.views.comments import post_comment
from datetime import datetime
from .models import Report, ReportComment
from .forms import ReportForm

class StudentHistoryView(LoginRequiredMixin, ListView):
    template_name = 'reports/student_history.html'
    context_object_name = 'reports'
    paginate_by = 10

    def get_queryset(self):
        # 获取指定学生的所有报告，按时间倒序排列
        student_id = self.kwargs['student_id']
        student = get_object_or_404(get_user_model(), id=student_id)
        return Report.objects.filter(student=student).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs['student_id']
        context['student'] = get_object_or_404(get_user_model(), id=student_id)
        return context

@permission_required('reports.can_view_all_reports')
def student_history(request, student_id):
    # 函数视图版本，与类视图功能相同
    student = get_object_or_404(get_user_model(), id=student_id)
    reports = Report.objects.filter(student=student).order_by('-created_at')
    return render(request, 'reports/student_history.html', {
        'reports': reports,
        'student': student
    })
class EmploymentStatsView(LoginRequiredMixin, TemplateView):  # 新增登录验证
    template_name = 'reports/employment_stats.html'

    # 可选：限制仅管理员/教师访问
    # permission_required = 'reports.view_report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. 按专业统计（容错处理：排除空值）
        major_stats = Report.objects.filter(
            student__student_profile__major__isnull=False  # 过滤专业为空的记录
        ).values('student__student_profile__major').annotate(
            job_count=Count('id', filter=Q(status='job')),
            intern_count=Count('id', filter=Q(status='intern')),
            signed_count=Count('id', filter=Q(status='signed')),
            other_count=Count('id', filter=Q(status='other'))
        ).order_by('student__student_profile__major')  # 排序确保一致性

        # 2. 按班级统计（容错处理：排除空值）
        class_stats = Report.objects.filter(
            student__student_profile__class_group__isnull=False  # 过滤班级为空的记录
        ).values('student__student_profile__class_group').annotate(
            job_count=Count('id', filter=Q(status='job')),
            intern_count=Count('id', filter=Q(status='intern')),
            signed_count=Count('id', filter=Q(status='signed')),
            other_count=Count('id', filter=Q(status='other'))
        ).order_by('student__student_profile__class_group')

        # 调试：打印数据（在终端查看是否有值）
        print("专业统计数据:", list(major_stats))
        print("班级统计数据:", list(class_stats))

        context.update({
            'major_stats': major_stats,
            'class_stats': class_stats,
            # 添加空数据标识，用于前端提示
            'has_major_data': len(major_stats) > 0,
            'has_class_data': len(class_stats) > 0,
        })
        return context


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10

    def test_func(self):
        # 允许教师或管理员查看所有报告，学生只能查看自己的
        return (self.request.user.has_perm('reports.can_view_all_reports') or
                self.request.user.groups.filter(name='Teachers').exists() or
                True)  # 学生总是可以通过自己的视图
    def get_queryset(self):
        queryset = Report.objects.filter(student=self.request.user)
        if self.request.user.has_perm('reports.can_view_all_reports'):
            queryset = Report.objects.all()
        return queryset.order_by('-created_at')


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'

    def get_object(self, queryset=None):
        try:
            # 先获取对象
            obj = super().get_object(queryset)

            # 检查权限
            if not (self.request.user == obj.student or
                    self.request.user.has_perm('reports.can_view_all_reports')):
                raise Http404("您没有权限查看此报告")

            return obj
        except Report.DoesNotExist:
            raise Http404("报告不存在")


class ReportCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'reports/report_form.html'
    success_url = reverse_lazy('reports:report_list')

    def test_func(self):
        # 只有学生可以创建报告
        return hasattr(self.request.user, 'student_profile')

    def form_valid(self, form):
        form.instance.student = self.request.user
        return super().form_valid(form)


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    form_class = ReportForm
    template_name = 'reports/report_form.html'
    success_url = reverse_lazy('reports:report_list')

    def get_queryset(self):
        # 确保用户只能修改自己的报告
        return Report.objects.filter(student=self.request.user)


@permission_required('reports.change_report')
@permission_required('reports.can_change_any_report')
@user_passes_test(lambda u: u.groups.filter(name='Teachers').exists())
def add_feedback(request, pk):
    """教师添加反馈视图"""
    report = get_object_or_404(Report, pk=pk)

    if request.method == 'POST':
        feedback = request.POST.get('feedback', '')
        report.feedback = feedback
        report.save()
        return redirect('reports:report_detail', pk=report.pk)

    # GET 请求时显示反馈表单
    return render(request, 'reports/feedback_form.html', {'report': report})


@permission_required('reports.view_report')
def export_reports(request):
    """导出报告为CSV文件"""
    # 创建HTTP响应对象，设置CSV头部
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="internship_reports.csv"'

    # 创建CSV writer
    writer = csv.writer(response)

    # 写入CSV头部
    writer.writerow([
        '学生', '学号', '周次', '实习单位', '岗位',
        '就业状态', '提交时间', '紧急状态', '教师反馈'
    ])

    # 获取报告数据
    reports = Report.objects.select_related('student').all()

    # 写入报告数据
    for report in reports:
        writer.writerow([
            report.student.username,
            getattr(report.student, 'student_id', 'N/A'),  # 修改此处
            report.week,
            report.company,
            report.position,
            report.get_status_display(),
            report.created_at.strftime("%Y-%m-%d %H:%M"),
            "紧急" if report.is_urgent else "正常",
            report.feedback[:100]  # 截取前100个字符
        ])

    return response


@permission_required('reports.change_report')
def add_comments_and_tags(request, pk):
    """教师添加评论和标记视图"""
    report = get_object_or_404(Report, pk=pk)

    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        tags = request.POST.get('tags', '')
        report.comments = comments
        report.tags = tags
        report.save()
        return redirect('reports:report_detail', pk=report.pk)

    # GET 请求时显示表单
    return render(request, 'reports/comments_tags_form.html', {'report': report})


def is_teacher(user):
    return user.is_teacher

@permission_required('reports.can_change_any_report')
@user_passes_test(is_teacher)  # 使用更新后的权限检查
def report_comments(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    # 处理POST请求
    if request.method == 'POST':
        comment_content = request.POST.get('comment', '').strip()
        if comment_content:
            ReportComment.objects.create(
                report=report,
                user=request.user,
                content=comment_content
            )
        return redirect('reports:report_comments', report_id=report.id)

    # 处理GET请求
    comments = report.report_comments.all().order_by('-created_at')
    return render(
        request,
        'reports/report_comments.html',
        {'report': report, 'comments': comments}
    )

@permission_required('reports.can_create_report')
def create_report(request):
    # 创建报告逻辑
    pass

def get_queryset(self):
    queryset = super().get_queryset()
    status = self.request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    return queryset


@permission_required('reports.can_view_all_reports')
def export_student_history(request, student_id):
    # 获取学生对象
    student = get_object_or_404(get_user_model(), id=student_id)

    # 获取该学生的所有报告
    reports = Report.objects.filter(student=student).order_by('-created_at')

    # 设置响应头，指定为CSV文件
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{student.username}_实习报告历史_{datetime.now().strftime("%Y%m%d")}.csv"'

    # 创建CSV writer
    writer = csv.writer(response)

    # 写入CSV头部
    writer.writerow([
        '周次', '实习单位', '岗位',
        '就业状态', '提交时间', '更新时间',
        '紧急状态', '教师反馈', '评论', '标记'
    ])

    # 写入报告数据
    for report in reports:
        writer.writerow([
            f'第{report.week}周',
            report.company or '',
            report.position or '',
            report.get_status_display(),
            report.created_at.strftime("%Y-%m-%d %H:%M"),
            report.updated_at.strftime("%Y-%m-%d %H:%M"),
            '是' if report.is_urgent else '否',
            report.feedback or '',
            report.comments or '',
            report.tags or ''
        ])

    return response