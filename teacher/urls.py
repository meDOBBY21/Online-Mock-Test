from django.urls import path
from . import views
from django.views.i18n import JavaScriptCatalog
urlpatterns=[
    path('review/',views.review,name='review'),
    path('edit/<int:id>',views.edit,name='edit'),
    path('edit_test/<int:test_id>/<int:id>',views.edit_test,name='edit_test'),
    path('test_entry',views.test_entry,name='test_entry'),
    path('question_entry/<int:test_id>/<str:topic>',views.questions_entry,name='questions_entry'),
    path('jsi18n',JavaScriptCatalog.as_view(),name='js-catlog'),
    path('preview/<int:test_id>',views.preview,name="preview"),
    path('edit_tests',views.edit_tests,name='edit_tests'),
    path('subject_questions',views.subject_questions,name='subject_questions'),
    path('test_results/<int:test_id>',views.test_results,name='test_results'),
    path('questions/',views.view_questions,name='questions'),
    path('remove_test/<int:test_id>',views.remove_test,name='remove_test'),
]