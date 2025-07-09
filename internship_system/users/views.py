# users/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .models import Student, Teacher, UserProfile
from .forms import StudentRegistrationForm, TeacherRegistrationForm
from django.contrib.auth import get_user_model, login

User = get_user_model()

# 新增：切换用户列表视图（仅管理员可访问）
class UserSwitchListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_switch.html'
    context_object_name = 'users'
    paginate_by = 20

    # 仅允许超级管理员访问
    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        return User.objects.all().order_by('username')

# 新增：执行切换用户的视图
def switch_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('users:login')

    target_user = get_object_or_404(User, id=user_id)
    # 记录原始用户ID到session
    request.session['original_user_id'] = request.user.id
    login(request, target_user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('reports:report_list')

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        # 管理员查看所有用户，普通用户只看到自己
        if self.request.user.is_superuser:
            return User.objects.all().order_by('date_joined')
        return User.objects.filter(id=self.request.user.id)

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

    def get_object(self):
        # 用户只能查看自己的详情，管理员可以查看所有
        if self.request.user.is_superuser:
            return super().get_object()
        return self.request.user


class StudentRegisterView(CreateView):
    form_class = StudentRegistrationForm
    template_name = 'users/register_student.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # 创建用户
        user = form.save(commit=False)
        user.is_teacher = False  # 明确设置为学生
        user.save()

        # 创建学生档案
        Student.objects.create(
            user=user,
            student_id=form.cleaned_data['student_id'],
            class_group=form.cleaned_data['class_group'],
            major=form.cleaned_data['major']
        )

        # 分配权限（通过信号自动处理）
        return redirect(self.success_url)


class TeacherRegisterView(CreateView):
    form_class = TeacherRegistrationForm
    template_name = 'users/register_teacher.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # 创建用户
        user = form.save(commit=False)
        user.is_teacher = True  # 明确设置为教师
        user.save()

        # 创建教师档案
        Teacher.objects.create(
            user=user,
            teacher_id=form.cleaned_data['teacher_id'],
            managed_classes=form.cleaned_data['managed_classes']
        )

        # 分配权限（通过信号自动处理）
        return redirect(self.success_url)

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            if hasattr(self.request.user, 'student'):
                context['student'] = self.request.user.student
            if hasattr(self.request.user, 'teacher'):
                context['teacher'] = self.request.user.teacher
        except Exception:
            pass
        return context

class RegisterView(CreateView):
    template_name = 'users/register_choice.html'
    success_url = reverse_lazy('users:login')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user_type = request.POST.get('user_type')
        if user_type == 'student':
            return redirect('users:register_student')
        elif user_type == 'teacher':
            return redirect('users:register_teacher')
        return redirect('users:register')
