from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Task, Comment
from .forms import TaskForm, TaskStatusForm, CommentForm
from projects.models import Project


@login_required
def dashboard(request):
    user = request.user
    if user.is_manager_role():
        all_tasks = Task.objects.all()
    else:
        all_tasks = Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).distinct()

    todo_count = all_tasks.filter(status='todo').count()
    in_progress_count = all_tasks.filter(status='in_progress').count()
    done_count = all_tasks.filter(status='done').count()
    overdue_tasks = [t for t in all_tasks if t.is_overdue()]

    my_tasks = Task.objects.filter(assigned_to=user, status__in=['todo', 'in_progress']).order_by('deadline')[:5]
    recent_tasks = all_tasks.order_by('-updated_at')[:8]

    active_projects = Project.objects.filter(status='active')
    if not user.is_manager_role():
        active_projects = active_projects.filter(
            Q(members=user) | Q(owner=user)
        ).distinct()

    context = {
        'todo_count': todo_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
        'overdue_count': len(overdue_tasks),
        'my_tasks': my_tasks,
        'recent_tasks': recent_tasks,
        'active_projects': active_projects,
        'total_tasks': all_tasks.count(),
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def task_list(request):
    user = request.user
    if user.is_manager_role():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).distinct()

    # Filters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    project_filter = request.GET.get('project', '')
    search_query = request.GET.get('q', '')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    projects = Project.objects.filter(status='active')
    context = {
        'tasks': tasks.select_related('project', 'assigned_to', 'created_by'),
        'projects': projects,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'project_filter': project_filter,
        'search_query': search_query,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'tasks/list.html', context)


@login_required
def kanban_board(request):
    user = request.user
    project_id = request.GET.get('project', '')

    if user.is_manager_role():
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(
            Q(assigned_to=user) | Q(created_by=user)
        ).distinct()

    if project_id:
        tasks = tasks.filter(project_id=project_id)

    todo_tasks = tasks.filter(status='todo').select_related('project', 'assigned_to')
    in_progress_tasks = tasks.filter(status='in_progress').select_related('project', 'assigned_to')
    done_tasks = tasks.filter(status='done').select_related('project', 'assigned_to')

    projects = Project.objects.filter(status='active')
    context = {
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'projects': projects,
        'project_filter': project_id,
    }
    return render(request, 'tasks/kanban.html', context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    if not user.is_manager_role() and task.assigned_to != user and task.created_by != user:
        messages.error(request, 'You do not have access to this task.')
        return redirect('task_list')

    status_form = TaskStatusForm(instance=task)
    comment_form = CommentForm()

    if request.method == 'POST':
        if 'update_status' in request.POST:
            status_form = TaskStatusForm(request.POST, instance=task)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, 'Task status updated.')
                return redirect('task_detail', pk=pk)
        elif 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.author = user
                comment.save()
                messages.success(request, 'Comment added.')
                return redirect('task_detail', pk=pk)

    context = {
        'task': task,
        'status_form': status_form,
        'comment_form': comment_form,
        'comments': task.comments.select_related('author'),
    }
    return render(request, 'tasks/detail.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully.')
            return redirect('task_detail', pk=task.pk)
    else:
        initial = {}
        project_id = request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        form = TaskForm(user=request.user, initial=initial)
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Create Task'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not request.user.is_manager_role() and task.created_by != request.user:
        messages.error(request, 'You can only edit tasks you created.')
        return redirect('task_detail', pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_detail', pk=pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Edit Task', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not request.user.is_manager_role() and task.created_by != request.user:
        messages.error(request, 'You can only delete tasks you created.')
        return redirect('task_detail', pk=pk)
    if request.method == 'POST':
        title = task.title
        project = task.project
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        if project:
            return redirect('project_detail', pk=project.pk)
        return redirect('task_list')
    return render(request, 'tasks/confirm_delete.html', {'task': task})
