from django.shortcuts import render, redirect, get_object_or_404
from takedata.models import *
from takedata.forms import *
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from takedata.forms import QuestionForm, ChoiceForm
from .forms import TestForm,QuestionType,AllQuestions
from student.models import Test
from django import forms
from login.models import StudentProfile, TeacherProfile
from django.forms import modelform_factory, modelformset_factory

# Create your views here.


def subject_questions(request):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    return render(request, 'teacher/subject_questions.html', {})


def test_results(request, test_id):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    test = Test.objects.get(id=test_id)
    attempted_students = {}
    for student in test.results.keys():
        attempted_students[student] = test.score[student]
    return render(request, 'teacher/test_results.html', {'students': attempted_students, 'test': test})


def review(request):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    questions = Question.objects.filter(approved=False)
    teacher = TeacherProfile.objects.get(username=request.user.username)
    for question in questions:
        topic = Topic.objects.get(topic=question.topic)
        if topic.subject.subject not in teacher.subjects:
            print('in', topic.subject, teacher.subjects)
            questions = questions.exclude(id=question.id)
    if request.method == 'POST':
        dictonary = dict(request.POST)
        d = list(request.POST.keys())
        l = d[1].split('_')
        id = int(l[0])
        question = get_object_or_404(Question, id=id)
        if dictonary[d[1]][0] == 'Accept':
            question.approved = True
            user = User.objects.get(username=question.username)
            if user.role == 'STUDENT':
                student = StudentProfile.objects.get(
                    username=question.username)
            else:
                student = TeacherProfile.objects.get(
                    username=question.username)
            if student:
                student.contrib_points += 1
                student.save()
            question.save()
            return redirect('/teacher/review')
        elif dictonary[d[1]][0] == 'Reject':
            question.delete()
            return redirect('review')
        else:
            return redirect('edit', id=question.id)
    if len(questions):
        msg = 1
    else:
        msg = 0
    return render(request, 'teacher/review.html', {'msg': msg, 'questions': questions})


def edit(request, id):
    if request.user.role != 'TEACHER':
        return redirect('/exam')

    question = get_object_or_404(Question, id=id)
    ChoiceFormSet = forms.modelformset_factory(
        Choice, form=ChoiceForm, extra=0)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(
            request.POST, queryset=question.choice_set.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('/teacher/review',)
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(queryset=question.choice_set.all())

    return render(request, 'teacher/edit.html', {'form': form, 'formset': formset})


def test_entry(request):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    teacher = TeacherProfile.objects.get(username=request.user.username)
    exam = Test()

    if request.method == 'POST':
        test = TestForm(teacher, request.POST)
        if test.is_valid():
            exam.name = test.cleaned_data['name']
            exam.questions = {'data': []}
            semester = test.cleaned_data['course']
            sem = int(semester[5])
            usernames = StudentProfile.objects.filter(semester=sem)
            usernames = usernames.filter(dept=teacher.dept)
            un = []
            for username in usernames:
                exam.modified[username.username] = 0
                un.append(username.username)
            exam.time = test.cleaned_data['time']
            exam.topic = test.cleaned_data['course']
            exam.usernames = {'usernames': un}
            exam.test_time = test.cleaned_data['test_duration']
            exam.by = teacher.username
            exam.save()

        test = TestForm(teacher=teacher)
        return redirect('questions_entry', test_id=exam.id, topic=semester)
    else:
        test = TestForm(teacher=teacher)

    return render(request, 'teacher/test_entry.html', {'test': test})


def remove_test(request, test_id):
    test = Test.objects.get(id=test_id)
    test.delete()
    if request.user.role=="TEACHER":
        return redirect('edit_tests')
    else:
        return redirect('old_tests')


def questions_entry(request, test_id, topic):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    teacher = TeacherProfile.objects.get(username=request.user.username)
    test = Test.objects.get(id=test_id)
    top = Topic.objects.get(topic=topic)
    type = request.GET.get('type')
    
    if type==None:
        typeform = QuestionType(type='MCQs')
    else:
        typeform = QuestionType(type=type)

    ChoiceFormSet = forms.modelformset_factory(
        Choice, form=ChoiceForm, extra=4)
    if type == 'Fill in the Blanks':
        ChoiceFormSet = forms.modelformset_factory(
            Choice, form=ChoiceForm, extra=1)
    if type == 'True or False':
        ChoiceFormSet = forms.modelformset_factory(
            Choice, form=ChoiceForm, extra=2)

    if request.method == 'POST':
        if not type:
            type = 'MCQs'
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        question = Question(question=request.POST.get('question'), marks=1, type=type)
        question.topic = top
        question.username = teacher.username
        question.save()
        if formset.is_valid():
            print("Valid formset")
            for choice_form in formset:
                if choice_form.cleaned_data:
                    choice = choice_form.save(commit=False)
                    choice.question = question
                    choice.save()
            question.approved = True
            question.save()
            data = test.questions['data']
            data.append(question.id)
            test.questions = {'data': data}
            test.save()
        if request.POST.get('submit') == 'Preview':
            return redirect('preview', test.id)
        else:
            form = QuestionForm()
            formset = ChoiceFormSet(queryset=Choice.objects.none())
    else:
        form = QuestionForm()
        formset = ChoiceFormSet(queryset=Choice.objects.none())

    return render(request, 'teacher/questions_entry.html', {'test_id': test_id, 'form': form, 'formset': formset,'typeform':typeform})


def preview(request, test_id):
    test = Test.objects.get(id=test_id)
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    questions = []
    teacher = TeacherProfile.objects.get(username=request.user.username)
    for q in test.questions['data']:
        question = Question.objects.get(id=q)
        questions.append(question)
    if request.method == 'POST':
        dictonary = dict(request.POST)
        d = list(request.POST.keys())
        l = d[len(d)-1].split('_')
        id = int(l[0])
        form = TestForm(teacher=teacher)
        form.fill(teacher=teacher, course=test.topic,
                  test_duration=test.test_time, name=test.name, time=test.time)
        print(d, 'HI')

        if form.is_valid():
            test.name = test.cleaned_data['name']
            test.questions = {'data': []}
            semester = test.cleaned_data['course']
            sem = int(semester[5])
            usernames = StudentProfile.objects.filter(semester=sem)
            usernames = usernames.filter(dept=teacher.dept)
            un = []
            for username in usernames:
                un.append(username.username)
            test.time = test.cleaned_data['time']
            test.usernames = {'usernames': un}
            test.test_time = test.cleaned_data['test_duration']
            test.save()
        attempted_students = list(test.results.keys())
        if attempted_students:
            for stu in attempted_students:
                test.modified[stu] = 1
        test.save()
        if dictonary[d[6]][0] == 'Remove':
            test.questions['data'].remove(id)
            test.save()
            return redirect('preview', test_id=test_id)
        elif dictonary[d[6]][0] == 'Edit':
            return redirect('edit_test', test_id=test.id, id=question.id)

    else:
        form = TestForm(teacher=teacher)
        form.fill(course=test.topic, test_duration=test.test_time,
                  name=test.name, time=test.time, teacher=teacher)
    return render(request, 'teacher/preview.html', { 'questions': questions, 'form': form, 'test': test})


def edit_test(request, test_id, id):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    question = get_object_or_404(Question, id=id)
    QuestionForm = modelform_factory(Question, fields=('question',), widgets={
                                     'question': forms.Textarea(attrs={'class': 'form-control', 'cols': 20, 'rows': 5})})
    ChoiceFormSet = modelformset_factory(Choice, fields=('choice', 'is_correct',), widgets={
        'choice': forms.TextInput(attrs={'class': 'form-control'}),
        'is_correct': forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input mt-0'})}, extra=0)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(
            request.POST, queryset=question.choice_set.all())
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('/teacher/preview/'+str(test_id))
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(queryset=question.choice_set.all())

    return render(request, 'teacher/edit.html', {'form': form, 'formset': formset})


def edit_tests(request):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    tests = Test.objects.all()
    teacher_tests = []
    for test in tests:
        if test.by == request.user.username:
            teacher_tests.append(test)
    return render(request, 'teacher/edit_tests.html', {'tests': teacher_tests})


def view_questions(request):
    if request.user.role != 'TEACHER':
        return redirect('/exam')
    subject = request.GET.get('subject')
    if subject==None:
        subject='All'
    teacher = TeacherProfile.objects.get(username=request.user.username)
    form =AllQuestions(teacher=teacher)
    form.fill(subject=subject,teacher=teacher)
    questions = Question.objects.none()
    for sub in teacher.subjects:
        questions = questions | Question.objects.filter(topic__subject=sub)
    questions = questions.filter(approved=True)
    topics = teacher.subjects
    if subject!='All':
        topics = [subject]
        questions = questions.filter(topic__subject=subject)
    return render(request, 'teacher/questions.html', {'questions': questions, 'subjects': teacher.subjects, 'topics': topics,'form':form})
