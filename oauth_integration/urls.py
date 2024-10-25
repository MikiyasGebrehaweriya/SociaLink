from django.urls import path
from . import views

app_name = 'oauth_integration'

urlpatterns = [
    path('instagram_login/', views.instagramAuthorize, name='instagram_authorize'),
    path('instagram_callback/', views.instagramCallback, name="instagramCallback"),
    path('facebook_login/', views.facebookAuthorize, name='facebook_authorize'),
    path('facebook_callback/', views.facebookCallback, name="facebookCallback"),
]