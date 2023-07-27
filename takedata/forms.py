from django import forms
from .models import Question,Choice

class QuestionType(forms.Form):
    question_type=forms.ChoiceField(choices=(('MCQs','MCQs'),
                                   ('Fill in the Blanks','Fill in the Blanks'),
                                   ('True or False','True or False')))

class QuestionForm(forms.ModelForm):
    question=forms.CharField(max_length=1000,required=False,widget=forms.Textarea(attrs={'class': 'form-control', 'cols': 20, 'rows': 5}))
    marks=forms.IntegerField()
    class Meta:
        model=Question
        fields=('question','marks')

class ChoiceForm(forms.ModelForm):
    class Meta:
        model=Choice
        fields=('choice','is_correct',)
        widgets={'choice': forms.TextInput(attrs={'class': 'form-control',
                                                  'name':'form-{{forloop.counter|add:"-1"}}-choice',
                                                  'id':'id_form-{{forloop.counter|add:"-1"}}-choice'}),
                 'is_correct': forms.CheckboxInput(attrs={'type': 'checkbox',
                                                          'class':'form-check-input mt-0',
                                                          'name':'form-{{forloop.counter|add:"-1"}}-is_correct',
                                                          'id':'id_form-{{forloop.counter|add:"-1"}}-is_correct'})}

class ExcelFileUpload(forms.Form):
    file=forms.FileField()


