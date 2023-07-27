from django import forms
from takedata.models import Question, Choice
from student.models import Test
from login.models import TeacherProfile
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime


class TestForm(forms.Form):
    course = forms.ChoiceField(choices=(), required=True)
    test_duration = forms.IntegerField()
    name = forms.CharField(max_length=50)

    time = forms.SplitDateTimeField(widget=AdminSplitDateTime())

    def fill(self, teacher, course, test_duration, name, time):
        choices = [(sub, sub) for sub in teacher.subjects]
        self.fields['course'].choices = choices
        self.fields['course'].initial = course
        self.fields['test_duration'].initial = test_duration
        self.fields['name'].initial = name
        self.fields['time'].initial = time

    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(sub, sub) for sub in teacher.subjects]
        self.fields['course'].choices = choices


class QuestionType(forms.Form):
    type = forms.ChoiceField(choices=(('MCQs', 'MCQs'),('Fill in the Blanks', 'Fill in the Blanks'),('True or False', 'True or False')),required=False)
    
    def fill(self,type):
        self.fields['type'].initial = type

    def __init__(self,type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].initial=type

class AllQuestions(forms.Form):
    subject=forms.ChoiceField(choices=())

    def fill(self, teacher, subject):
        choices = [(sub, sub) for sub in teacher.subjects]
        choices.append(('All','All'))
        self.fields['subject'].choices = choices
        self.fields['subject'].initial = subject

    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(sub, sub) for sub in teacher.subjects]
        choices.append(('All','All'))
        self.fields['subject'].choices = choices