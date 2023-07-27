from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm,PasswordChangeForm
from .models import *


class StudentForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ['username', 'dept', 'name',]


class TeacherForm(UserCreationForm):
    class Meta:
        model = Teacher
        fields = ['username', 'dept', 'name',]


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class SubjectsWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if not value:
            value = []
        return forms.widgets.TextInput(attrs).render(name, ', '.join(value), attrs, renderer)

class TeacherProfileForm(forms.ModelForm):
    subjects = forms.CharField(
        label='Subjects',
        widget=SubjectsWidget(attrs={'placeholder': 'Enter comma separated subjects'}),  
        required=False,
    )

    class Meta:
        model = TeacherProfile
        fields = ['username', 'name', 'subjects', 'contrib_points']

class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model=User
        fields = ['old_password', 'new_password1', 'new_password2']

class FilterForm(forms.Form):
    sem=forms.ChoiceField(choices=(('all','all'),
                                   (1,1),
                                   (2,2),
                                   (3,3),
                                   (4,4),
                                   (5,5),
                                   (6,6)
                                   ))
    dep=forms.ChoiceField(choices=(('all','all'),
                                   ('DMACS','DMACS'),
                                   ('DMAC','DMAC')
                                   ))
    
    def __init__(self,dep,sem, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sem'].initial=sem
        self.fields['dep'].initial=dep