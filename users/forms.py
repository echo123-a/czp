from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Student, Teacher

class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20, label="学号")
    class_group = forms.CharField(max_length=50, label="班级")
    major = forms.CharField(max_length=100, label="专业")

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': '用户名',
            'email': '电子邮箱',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            student_id = self.cleaned_data.get('student_id')
            class_group = self.cleaned_data.get('class_group')
            major = self.cleaned_data.get('major')
            Student.objects.create(
                user=user,
                student_id=student_id,
                class_group=class_group,
                major=major
            )
        return user

class TeacherRegistrationForm(UserCreationForm):
    teacher_id = forms.CharField(max_length=20, label="教师工号")
    managed_classes = forms.CharField(
        max_length=255,
        label="管理班级",
        help_text="多个班级用逗号分隔"
    )

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': '用户名',
            'email': '电子邮箱',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            teacher_id = self.cleaned_data.get('teacher_id')
            managed_classes = self.cleaned_data.get('managed_classes')
            Teacher.objects.create(
                user=user,
                teacher_id=teacher_id,
                managed_classes=managed_classes
            )
        return user