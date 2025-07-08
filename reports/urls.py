# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'  # 添加命名空间

urlpatterns = [
    # 报告列表
    path('', views.ReportListView.as_view(), name='report_list'),

    # 报告详情
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),

    # 创建报告
    path('create/', views.ReportCreateView.as_view(), name='report_create'),

    # 更新报告
    path('<int:pk>/update/', views.ReportUpdateView.as_view(), name='report_update'),

    # 添加反馈
    path('<int:pk>/feedback/', views.add_feedback, name='add_feedback'),

    # 导出报告
    path('export/', views.export_reports, name='export_reports'),

    path('employment-stats/', views.EmploymentStatsView.as_view(), name='employment_stats'),

    # 添加评论和标记
    path('<int:pk>/comments-tags/', views.add_comments_and_tags, name='add_comments_and_tags'),

    path('<int:report_id>/comments/', views.report_comments, name='report_comments'),
    # 学生历史记录
    path('student/<int:student_id>/history/', views.StudentHistoryView.as_view(), name='student_history'),

    path('student/<int:student_id>/history/',
         views.StudentHistoryView.as_view(),
         name='student_history'),
    path('student/<int:student_id>/history/export/',
         views.export_student_history,
         name='export_student_history'),
]