from django.contrib import admin
from django.urls import reverse
from .models import *
from .forms import *
from import_export.admin import ImportExportModelAdmin

# Register your models here.

admin.site.register(User)
class StudentAdmin(admin.ModelAdmin):
    form=StudentForm
class TeacherAdmin(admin.ModelAdmin):
    form=TeacherForm
class TeacherProfileAdmin(admin.ModelAdmin):
    form = TeacherProfileForm

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            subjects = form.cleaned_data['subjects']
            if subjects:
                obj.subjects = [subject.strip() for subject in subjects.split(',')]
        super().save_model(request, obj, form, change)

admin.site.register(TeacherProfile, TeacherProfileAdmin)
admin.site.register(StudentProfile)
admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher,TeacherAdmin)

class ViewAdmin(ImportExportModelAdmin):
    pass