from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('developer', 'Developer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')
    avatar_color = models.CharField(max_length=7, default='#6366f1')

    def is_admin_role(self):
        return self.role == 'admin'

    def is_manager_role(self):
        return self.role in ('admin', 'manager')

    def get_initials(self):
        parts = self.get_full_name().split()
        if parts:
            return ''.join(p[0].upper() for p in parts[:2])
        return self.username[0].upper()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
