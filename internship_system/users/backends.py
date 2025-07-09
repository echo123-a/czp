# users/backends.py

from django.contrib.auth.backends import ModelBackend


class RoleBackend(ModelBackend):
    """自定义角色认证后端"""

    def get_user_role(self, user):
        """获取用户角色"""
        if hasattr(user, 'student'):
            return 'student'
        elif hasattr(user, 'teacher'):
            return 'teacher'
        return None

    def has_perm(self, user_obj, perm, obj=None):
        """自定义权限检查"""
        # 首先检查默认权限
        if super().has_perm(user_obj, perm, obj):
            return True

        # 根据角色添加额外权限
        role = self.get_user_role(user_obj)

        # 教师权限
        if role == 'teacher':
            teacher_perms = [
                'reports.view_weeklyreport',
                'reports.change_weeklyreport',
                'reports.add_feedback',
            ]
            if perm in teacher_perms:
                return True

        # 学生权限
        elif role == 'student':
            student_perms = [
                'reports.add_weeklyreport',
                'reports.view_own_weeklyreport',
            ]
            if perm in student_perms:
                return True

        return False