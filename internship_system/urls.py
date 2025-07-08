# internship_system/urls.py

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from core.admin import custom_admin_site
from core.views import CustomLoginView  # 导入自定义登录视图


urlpatterns = [
    # 自定义登录页面
    path('login/', CustomLoginView.as_view(), name='login'),

    # 登出功能
    path('logout/', LogoutView.as_view(), name='logout'),

    # 管理后台
    path('admin/', custom_admin_site.urls),

    # 核心应用路由
    path('', include('core.urls')),

    # 报告管理路由
    path('api/v1/reports/', include('reports.urls')),

    # 用户管理路由
    path('api/v1/users/', include('users.urls')),

    # 移除以下行，不再使用内置认证路由
    # path('auth/', include('django.contrib.auth.urls')),

    # 首页，指向登录页面
    path('', CustomLoginView.as_view(), name='home'),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)