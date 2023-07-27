from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render,redirect
from login.models import StudentProfile,TeacherProfile, User
from .models import Test
from takedata.models import Question,Choice,Semester,Subject,Topic
from django.contrib.auth.decorators import login_required
import random
from .forms import DifficultyForm
from datetime import datetime
from django.template.defaulttags import register

def due_tests(request):
    if request.POST.get('button')=='Check Tests':
        tests=Test.objects.all().order_by('id')
        tests_to_take=[]
        for test in tests:
            if request.user.username in test.usernames['usernames'] and (len(test.usernames['usernames'])==1):
                keys=list(test.results.keys())
                if request.user.username not in keys:
                    tests_to_take.append(test)
        if len(tests_to_take):
            msg=1
        else:
            msg=0
        return render(request,'mcqs/duetests.html',{'tests':tests_to_take,'msg':msg,}) 
    elif request.POST.get('button')=='Create Test':
        return redirect('test_semester')
    return render(request, 'mcqs/due_tests.html', {})

def semester(request):
    student=StudentProfile.objects.get(username=request.user.username)
    semesters=Semester.objects.filter(semester__lte=student.semester)
    if request.GET.get('semester'):
        url='subject/'+str(request.GET.get('semester'))
        return redirect(url)
    return render(request, 'mcqs/semester.html', {'semesters': semesters,})

def subject(request, semester):
    sem = Semester.objects.get(semester=semester)
    if request.user.dept == 'DMACS':
        subjects=Subject.objects.filter(subject__icontains='UCSH')
    else:
        subjects=Subject.objects.filter(subject__icontains='UBBA')
    subjects = subjects.filter(semester=sem)
    return render(request, 'mcqs/subject.html', {'semester': sem, 'subjects': subjects,})

def topic(request, semester, subject):   
    if request.method=='POST':
        d=dict(request.POST)
        topics=''
        for topic in d['topic']:
            topics+=(topic+',')
        print(topics)
        return redirect('confirm',semester=semester,subject=subject,topic=topics)
    sem = Semester.objects.get(semester=semester)
    sub = Subject.objects.get(subject=subject)
    topics = Topic.objects.filter(semester=sem, subject=sub).exclude(topic=subject)
    return render(request, 'mcqs/topic.html', {'semester': sem, 'subject': sub, 'topics': topics,})

def test(request,semester,subject,topic):
    questions=[]
    no_of_questions=request.GET.get("questions")
    difficulty=request.GET.get("difficulty")
    if difficulty==None:
        difficulty=1
    if no_of_questions==None:
        no_of_questions=10
    form=DifficultyForm(diff=difficulty,ques=no_of_questions)
    if topic == 'all' and subject=='all':
        if request.user.dept == 'DMACS':
            subjects=Subject.objects.filter(subject__icontains='UCSH')
        else:
            subjects=Subject.objects.filter(subject__icontains='UBBA')
        for sub in subjects:
            top=Topic.objects.filter(subject=sub)
            for t in top:
                q=Question.objects.filter(topic=t)
                q=list(q.filter(approved=True))
                questions.extend(q)
    elif topic== 'all':
        top= Topic.objects.filter(semester=semester,subject=subject)
        for t in top:
            print(t)
            q=Question.objects.filter(topic=t)
            q=list(q.filter(approved=True))
            questions.extend(q)
    else:
        topics=topic.split(',')
        for t in topics:
            q=Question.objects.filter(topic=t)
            q=list(q.filter(approved=True))
            questions.extend(q)
    if request.method=='GET':
        if no_of_questions:
            no_of_questions=int(no_of_questions)
            if len(questions)>no_of_questions:
                questions=random.sample(questions,no_of_questions)
        else:
            if len(questions)>10:
                questions=random.sample(questions,'10')
        if questions:
            random.shuffle((questions))
            data=[]
            for question in questions:
                data.append(
                    question.id
                )
            usernames=[]
            usernames.append(request.user.username)
            xam=Test(questions={'data':data},usernames={'usernames':usernames})
            xam.name=str(semester)+'-'+subject+'-'+topic
            xam.time=datetime.now()
            xam.by=request.user.username
            if topic=='all' and subject=='all':
                xam.topic=semester
            else:
                xam.topic=subject
            if difficulty:
                difficulty=int(difficulty)
                xam.test_time=len(questions)*((7-difficulty)/6)
            else:
                xam.test_time=len(questions)
            xam.modified[request.user.username]=0
            xam.save()
            msg=1
            return render(request, 'mcqs/take_test.html', {'test_id':xam.id,'msg':msg,"form":form})
        else:
            msg=0
            return render(request, 'mcqs/take_test.html', {'msg':msg,})
    else:
        return render(request,'mcqs/take_test.html',{})

def take_test(request,test_id):
    test=Test.objects.get(id=test_id)
    if request.user.username in test.usernames['usernames']:
        reviewed=list(test.results.keys())
        if request.user.username not in reviewed:
            questions_set=[]
            for question in test.questions['data']:
                question=Question.objects.get(id=question)
                questions_set.append(question)
            min=1000*60
            duration=test.test_time*min
            return render(request,'mcqs/test.html',{'questions':questions_set,'test_id':test_id,'duration':duration})
        else:
            return redirect('/home')
    else:
        return redirect('/home')

def check_answers(request,test_id,username):
    score = 0
    test_data={}
    user=User.objects.get(username=username)
    if user.role=='STUDENT':
        user=StudentProfile.objects.get(username=username)
    else:
        user=TeacherProfile.objects.get(username=username)
    count=0
    questions_in_test=[]
    xam=Test.objects.get(id=test_id)

    count=len(xam.questions['data'])
    reviewed=list(xam.results.keys())
    if user.username not in reviewed or xam.modified[user.username]:
        for question in xam.questions['data']:
            q= Question.objects.get(id=question)
            for choice in q.choice_set.all():
                if choice.is_correct:
                    correct_choice=str(choice.choice)
            if request.user.username not in reviewed:
                choice=request.POST.get('choice_' + str(q.id),'Not Attempted')
                if choice=='':
                    choice='Not Attempted'
            else:
                results=xam.results[user.username]
                choice=results[str(question)]
        
            test_data[str(q.id)]=choice
            questions_in_test.append(q)
            if choice.lower()==correct_choice.lower():
                score += q.marks
        xam.reviewed=True
        if xam.modified[user.username]==1:
            if user.username in xam.score.keys():
                user.points-=xam.score[user.username]
                user.save()
            xam.modified[user.username]=0
        xam.score[user.username]=score
        xam.results[str(user.username)]=test_data
        xam.save()
        user.points+=score
        user.save()
        test_data=xam.results[str(user.username)]
    else:
        if user.username in xam.usernames['usernames']:
            score=xam.score[user.username]
            test_data=xam.results[str(user.username)]
            for question in test_data.keys():
                try:
                    q = Question.objects.get(id=question)
                except Question.DoesNotExist:
                    q=None
                if q is not None:
                    questions_in_test.append(q)
    context = {'score': score,'total':count,'questions':questions_in_test,'test_data':test_data,}
    return render(request, 'mcqs/result.html', context)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

def teachertest(request):
    tests=Test.objects.all().order_by('id')
    tests_to_take=[]
    for test in tests:
        if request.user.username in test.usernames['usernames'] and len(test.usernames['usernames'])>1:
            keys=list(test.results.keys())
            if request.user.username not in keys:
                tests_to_take.append(test)
    if tests_to_take:
        msg=1
    else:
        msg=0
    return render(request,'mcqs/duetests.html',{'msg':msg,'tests':tests_to_take,}) 

def old_tests(request):
    tests=Test.objects.all()
    user_tests=[]
    for test in tests:
        users=list(test.results.keys())
        if request.user.username in users:
            user_tests.append(test)
    return render(request,'mcqs/old_tests.html',{'tests':user_tests,})


