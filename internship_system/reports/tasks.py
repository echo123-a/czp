# reports/tasks.py
from django.core.mail import send_mail
from django.conf import settings
from .models import Report
from users.models import Teacher, Student

def send_reminders():
    # 获取未提交报告的学生
    students = Student.objects.all()
    for student in students:
        reports = Report.objects.filter(student=student.user)
        # 这里可以根据具体的业务逻辑判断是否需要提醒
        if not reports:
            subject = '实习报告提醒'
            message = f'{student.user.username}，你还未提交实习报告，请尽快提交。'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [student.user.email]
            send_mail(subject, message, from_email, recipient_list)

    # 也可以给教师发送提醒，例如有紧急报告时
    teachers = Teacher.objects.all()
    for teacher in teachers:
        urgent_reports = Report.objects.filter(is_urgent=True)
        if urgent_reports:
            subject = '紧急实习报告提醒'
            message = f'{teacher.user.username}，有紧急实习报告需要处理，请尽快查看。'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [teacher.user.email]
            send_mail(subject, message, from_email, recipient_list)