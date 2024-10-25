from django.urls import path
from . import views

app_name = 'content_management'

urlpatterns = [
    path("create/", views.create, name="create"),
    path("update/<int:pk>/", views.update, name="update"),
    path("delete/<int:pk>/", views.delete, name="delete"),
]