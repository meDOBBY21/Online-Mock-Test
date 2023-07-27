from django.urls import path
from . import views
# from takedata import views as takedata_views

urlpatterns=[
    path('',views.admin,name="admin_site"),
    path('exam',views.UserLogin.as_view(),name='login'),
    path('home',views.home,name='home'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('leaderboard',views.leaderboard,name='leaderboard'),
    path('change_theme',views.change_theme,name='change_theme'),
    path('password_change',views.password_change,name='password_change'),
]