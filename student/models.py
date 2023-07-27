from django.db import models
from datetime import timedelta
from takedata.models import Question

class Test(models.Model):
    usernames=models.JSONField(default=dict,blank=True)
    time=models.DateTimeField(default=None,blank=True)
    name=models.CharField(max_length=50,blank=True,default='')
    questions=models.JSONField(blank=True,default=dict)
    results=models.JSONField(verbose_name='Test Results',default=dict)
    score=models.JSONField(default=dict)
    modified=models.JSONField(blank=True,default=dict)
    test_time=models.FloatField(blank=True,default=5)
    topic=models.CharField(max_length=10,blank=True,default='')
    by=models.CharField(max_length=10,blank=True,default='')
    def __str__(self):
        return (str(self.name))

    
