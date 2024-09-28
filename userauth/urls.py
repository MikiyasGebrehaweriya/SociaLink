from django.urls import path
from . import views

urlpatterns = [
    path('', views.signIn, name="signIn"),
    path('signUp/', views.signUp, name="signUp"),
    path('signOut/', views.signOut, name="signOut"),
    path('termsAndconditions/', views.termsAndconditions, name="termsAndconditions"),
    path('completeProfile/', views.completeProfile, name="completeProfile"),
    path('instagram_login/', views.instagramAuthorize, name='instagram_authorize'),
    path('instagram_callback/', views.instagramCallback, name="instagramCallback"),
    path('facebook_callback/', views.facebookCallback, name="facebookCallback"),
    #path('facebook_login/', views.facebookAuthorize, name='facebook_authorize'),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("ai/", views.ai, name="ai"),
    path("members/", views.members, name="members"),
    path("connect/<str:username>/", views.connect, name="connect"),
    path("create/", views.create, name="create"),
    path("Update_profile/", views.update_profile, name="update_profile"),
    path("delete/<int:pk>/", views.delete, name="delete"),
    path("update/<int:pk>/", views.update, name="update"),
    path('report-csp-violation/', views.report_csp_violation, name='report_csp_violation'),
]
