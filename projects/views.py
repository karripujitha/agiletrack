from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm


@login_required
def project_list(request):
    if request.user.is_manager_role():
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(members=request.user) | Project.objects.filter(owner=request.user)
        projects = projects.distinct()
    return render(request, 'projects/list.html', {'projects': projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not request.user.is_manager_role() and request.user not in project.members.all() and project.owner != request.user:
        messages.error(request, 'You do not have access to this project.')
        return redirect('project_list')
    tasks = project.tasks.all()
    todo_tasks = tasks.filter(status='todo')
    in_progress_tasks = tasks.filter(status='in_progress')
    done_tasks = tasks.filter(status='done')
    return render(request, 'projects/detail.html', {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
    })


@login_required
def project_create(request):
    if not request.user.is_manager_role():
        messages.error(request, 'Only managers and admins can create projects.')
        return redirect('project_list')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/form.html', {'form': form, 'title': 'Create Project'})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not request.user.is_manager_role():
        messages.error(request, 'Only managers and admins can edit projects.')
        return redirect('project_list')
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/form.html', {'form': form, 'title': 'Edit Project', 'project': project})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not request.user.is_admin_role():
        messages.error(request, 'Only admins can delete projects.')
        return redirect('project_list')
    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'Project "{name}" deleted.')
        return redirect('project_list')
    return render(request, 'projects/confirm_delete.html', {'project': project})
