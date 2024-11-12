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
]
