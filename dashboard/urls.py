from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('login/', views.loginAdmin, name='login'),
    path('', views.index, name='home'),
    path('questions/', views.Questions, name='questions'),
    path('contestants/', views.Contestants, name='contestants'),
    path('logout', views.LogoutOut, name='logout'),
  
]