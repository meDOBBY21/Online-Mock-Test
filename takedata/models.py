from django.db import models
import random
from login.models import User

class Semester(models.Model):
    semester = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.semester)

class Subject(models.Model):
    subject = models.CharField(max_length=50,primary_key=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,db_column='semester')

    def __str__(self):
        return self.subject

class Topic(models.Model):
    topic = models.CharField(max_length=50,primary_key=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,db_column='semester')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,db_column='subject')

    def __str__(self):
        return self.topic

class Question(models.Model):
    question = models.TextField(max_length=1000)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,related_name='topic_name',db_column='topic')
    approved=models.BooleanField(default=False)
    username=models.CharField(default='',blank=True,max_length=10)
    marks=models.FloatField(default=1,blank=True)
    type=models.CharField(choices=(('MCQs','MCQs'),
                                   ('Fill in the Blanks','Fill in the Blanks'),
                                   ('True or False','True or False')),max_length=50,blank=True,default='MCQs')
    def get_choices(self):
        choices=list(Choice.objects.filter(question=self))
        random.shuffle((choices))
        data=[]
        for choice in choices:
            data.append({
                "choice":choice.choice,
                "is_correct":choice.is_correct
                })
        return data
    
    def __str__(self):
        return self.question

class Choice(models.Model):
    choice = models.CharField(max_length=500,null=True,blank=True)
    question = models.ForeignKey(Question, on_delete= models.CASCADE)
    is_correct=models.BooleanField(blank=True,null=True)

    
    def __str__(self):
        return self.choice

