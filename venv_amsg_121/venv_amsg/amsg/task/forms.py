from django import forms
from accounts.models import Class, CustomUser
from task.models import Question, Task


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_auth', 'user_grade', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassCreateForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ('class_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('task_name', 'task_subject',
                  'task_smallsubject', 'task_score',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('q_statement', 'q_answer', 'q_point', 'q_autostatus')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TaskSetForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('task_time',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
