# reports/forms.py
from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['week', 'company', 'position', 'status', 'content', 'problems','comments', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': '详细描述本周实习内容和进展...'}),
            'problems': forms.Textarea(attrs={'rows': 3, 'placeholder': '描述实习中遇到的问题和困难...'}),
        }
        labels = {
            'week': '周次',
            'company': '实习单位',
            'position': '岗位',
            'status': '就业状态',
            'content': '实习内容与进展',
            'problems': '遇到的问题',
            'comments': '教师反馈',
            'tags': '标签',
        }
        help_texts = {
            'week': '请输入当前实习周数（1-52）',
            'status': '选择你当前的就业状态',
        }