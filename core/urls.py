# core/urls.py

from django.urls import path
from . import views
from .views import TeacherDashboardView

app_name = 'core'



urlpatterns = [
    # path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
    path('admin/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
]

