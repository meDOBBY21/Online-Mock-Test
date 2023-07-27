from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STUDENT = "STUDENT", 'Student'
        TEACHER = "TEACHER", 'Teacher'
    base_role = Role.ADMIN
    dept = models.CharField(choices=(('DMACS', 'DMACS'),
                                     ('DMAC', 'DMAC')), max_length=10, blank=True)

    role = models.CharField(max_length=50, choices=Role.choices)
    name = models.CharField(max_length=50, blank=True)
    theme = models.CharField(max_length=50,choices=(('dark','dark'),('white','white')),default='white',blank=True)

    def change_theme(self, *args, **kwargs):
        if self.theme == 'white':
            self.theme='dark'
        else:
            self.theme='white'
        return super().save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)
    
    def change_password(self,pswd,*args,**kwargs):
        self.set_password(raw_password=pswd)
        return super().save(*args,**kwargs)


class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.STUDENT)


class Student(User):
    base_role = User.Role.STUDENT

    student = StudentManager()

    class Meta:
        proxy = True


class TeacherManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.TEACHER)


class Teacher(User):
    base_role = User.Role.TEACHER

    teacher = TeacherManager()

    class Meta:
        proxy = True


@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "STUDENT":
        StudentProfile.objects.create(
            user=instance, username=instance.username, name=instance.name,dept=instance.dept)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)
    dept=models.CharField(max_length=10,blank=True,default='DMACS')
    semester=models.IntegerField(choices=((1,1),
                                       (2,2),
                                       (3,3),
                                       (4,4),
                                       (5,5),
                                       (6,6),),blank=True,default=1)
    points = models.IntegerField(default=0)
    contrib_points = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=Teacher)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "TEACHER":
        TeacherProfile.objects.create(
            user=instance, username=instance.username, name=instance.name,dept=instance.dept)


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)
    dept=models.CharField(max_length=10,blank=True,default='DMACS')
    subjects = models.JSONField(blank=True,default=dict)
    points = models.IntegerField(default=0)
    contrib_points = models.IntegerField(default=0,blank=True)

    def __str__(self):
        return str(self.user)
