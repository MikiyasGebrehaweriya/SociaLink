from django.urls import path
from . import views

urlpatterns = [
    path('', views.signIn, name="signIn"),
    path('signUp/', views.signUp, name="signUp"),
    path('signOut/', views.signOut, name="signOut"),
    path('termsAndconditions/', views.termsAndconditions, name="termsAndconditions"),
    path('completeProfile/', views.completeProfile, name="completeProfile"),
    path('instagram_callback/', views.instagramCallback, name="instagramCallback"),
    path('facebook_callback/', views.facebookCallback, name="facebookCallback"),
    path("profile/<str:username>/", views.profile, name="profile"),
]
