from django.contrib import admin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'project', 'assigned_to', 'deadline', 'created_at')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description')
    list_editable = ('status', 'priority')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('author',)
