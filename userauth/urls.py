from django.urls import path
from . import views

app_name = 'userauth'

urlpatterns = [
    path('', views.sign_in, name="signIn"),
    path('signUp/', views.sign_up, name="signUp"),
    path('signOut/', views.sign_out, name="signOut"),
    path('termsAndconditions/', views.terms_and_conditions, name="termsAndconditions"),
    path('completeProfile/', views.complete_profile, name="completeProfile"),
    path('report-csp-violation/', views.report_csp_violation, name='report_csp_violation'),
    # path('instagram_login/', views.instagramAuthorize, name='instagram_authorize'),
    # path('instagram_callback/', views.instagramCallback, name="instagramCallback"),
    # path('facebook_callback/', views.facebookCallback, name="facebookCallback"),
    # path("profile/<str:username>/", views.profile, name="profile"),
    # path("ai/", views.ai, name="ai"),
    # path("members/", views.members, name="members"),
    # path("create/", views.create, name="create"),
    # path("Update_profile/", views.update_profile, name="update_profile"),
    # path("connect/<str:username>/", views.connect, name="connect"),
    # path("delete/<int:pk>/", views.delete, name="delete"),
    # path("update/<int:pk>/", views.update, name="update"),
]

#path('facebook_login/', views.facebookAuthorize, name='facebook_authorize'),