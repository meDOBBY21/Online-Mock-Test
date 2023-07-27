from django.shortcuts import render,redirect
from django.template.loader import get_template
from weasyprint import HTML,CSS
from django.http import HttpResponse
from django.urls import reverse_lazy
from .models import User,Student,Teacher,StudentProfile,TeacherProfile
from .forms import UserLoginForm,PasswordChangeForm,FilterForm
from django.contrib.auth.views import LoginView,LogoutView,PasswordChangeView
from django.contrib import messages

class UserLogin(LoginView):
    authentication_form=UserLoginForm
    template_name='login/login.html'
    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'error_message': 'Invalid username or password'})


def home(request):
    if request.user.role=='ADMIN':
        return redirect("/admin")
    if request.user.role=='TEACHER':
        dict={'students_p':StudentProfile.objects.all().order_by('-points'),'students_c':StudentProfile.objects.all().order_by('-contrib_points')}
        return render(request,'teacher/home.html',dict)
    else:
        dict={'students_p':StudentProfile.objects.all().order_by('-points'),'students_c':StudentProfile.objects.all().order_by('-contrib_points')}
        return render(request,'login/home.html',dict)

class UserLogout(LogoutView):
    template_name='login/login.html'

def change_theme(request):
    user=User.objects.get(username=request.user.username)
    user.change_theme()
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

def password_change(request):
    user=User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form=PasswordChangeForm(user=user,data=request.POST)
        if form.is_valid():
            user.change_password(request.POST.get('new_password1'))
            return redirect('home')
    else:
        form=PasswordChangeForm(user=user)
    return render(request,'login/password_change.html',{'form':form})

def leaderboard(request):
    dep = request.GET.get('dep')
    sem = request.GET.get('sem')
    print(dep,sem)
    if dep == None and sem == None:
        filter=FilterForm(sem='all',dep='all')
    elif dep == None:
        filter=FilterForm(dep='all',sem=sem)
    elif sem == None:
        filter=FilterForm(sem='all',dep=dep)
    else:
        filter=FilterForm(sem=sem,dep=dep)

    students = StudentProfile.objects.all()
    if dep!='all' and dep!=None:
        students = students.filter(dept=dep)
    if sem!='all' and sem!=None:
        students = students.filter(semester=sem)
    
    students_p = students.order_by('-points')
    students_c = students.order_by('-contrib_points')
    return render(request,'login/leaderboard.html',{'students_c':students_c,'students_p':students_p,'filter':filter})


def admin(request):
    if request.user.role=="ADMIN":
        return render(request,"login/data_entry.html",{})
    return redirect("login")


