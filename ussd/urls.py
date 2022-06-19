from django.urls import path

from . import views

app_name = 'ussd'
urlpatterns = [
    path('', views.ussdvote, name='index'),  # ussdvote  
    #wenhook post
    path('webhook', views.verify_payment, name='wenhook'),
    path('manual/verify', views.manualverify, name='manualverify'),
]