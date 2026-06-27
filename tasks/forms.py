from django import forms
from .models import Task, Comment
from accounts.models import User
from projects.models import Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'status', 'priority', 'project', 'assigned_to', 'deadline')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.all()
        self.fields['assigned_to'].empty_label = 'Unassigned'
        self.fields['project'].queryset = Project.objects.filter(status='active')
        self.fields['project'].empty_label = 'No Project'
        if user and not user.is_manager_role():
            self.fields['assigned_to'].queryset = User.objects.filter(id=user.id)


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('status',)
        widgets = {'status': forms.Select(attrs={'class': 'form-select form-select-sm'})}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add a comment...'
            })
        }
