from django import forms

class DifficultyForm(forms.Form):
    difficulty=forms.ChoiceField(choices=((1,1),
                                          (2,2),
                                          (3,3),
                                          (4,4),
                                          (5,5),
                                          (6,6)))
    questions=forms.IntegerField()

    def __init__(self,diff,ques, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['difficulty'].initial=diff
        self.fields['questions'].initial=ques