from django.urls import path
from . import views


urlpatterns = [
    path('',views.due_tests,name='due_tests'),
    path('semester',views.semester,name="test_semester"),
    path('subject/<int:semester>/', views.subject, name='test_subject'),
    path('topic/<int:semester>/<str:subject>/', views.topic, name='test_topic'),
    path('mcqs/<int:test_id>',views.take_test,name='test'),
    path('teachertest/',views.teachertest,name='teachertest'),
    path('confirm/<int:semester>/<str:subject>/<str:topic>', views.test, name='confirm'),
    path('results/<int:test_id>/<str:username>',views.check_answers,name='check_answers'),
    path('old_tests',views.old_tests,name='old_tests'),
]
