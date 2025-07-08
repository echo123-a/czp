from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),

    # 注册相关路由
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register/student/', views.StudentRegisterView.as_view(), name='register_student'),
    path('register/teacher/', views.TeacherRegisterView.as_view(), name='register_teacher'),

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # 修改退出登录视图，添加 next_page 参数
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'),

    # 新增：切换用户相关路由
    path('switch/', views.UserSwitchListView.as_view(), name='user_switch_list'),
    path('switch/<int:user_id>/', views.switch_user, name='switch_user'),
]