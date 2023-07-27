from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='semester'),
    path('give_subject/',views.take_subject,name='read_subject_data'),
    path('give_topic/',views.take_topic,name='read_topic_data'),
    path('subject/<int:semester>/', views.subject, name='subject'),
    path('topic/<int:semester>/<str:subject>/', views.topic, name='topic'),
    path('question_type/<int:semester>/<str:subject>/<str:topic>/', views.question_type, name='question_type'),
    path('question/<int:id>/', views.question, name='question'),
]
