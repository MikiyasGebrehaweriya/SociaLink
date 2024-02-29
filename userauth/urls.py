from django.urls import path
from . import views

urlpatterns = [
    path('', views.signIn, name="signIn"),
    path('signUp/', views.signUp, name="signUp"),
    path('completeProfile/', views.completeProfile, name="completeProfile"),
]
