from django.db import models
from accounts.models import User


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def task_count(self):
        return self.tasks.count()

    def completed_task_count(self):
        return self.tasks.filter(status='done').count()

    def progress_percent(self):
        total = self.task_count()
        if total == 0:
            return 0
        return int((self.completed_task_count() / total) * 100)
