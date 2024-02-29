from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=200, null=True)
    bio = models.TextField(null=True)
    profilePicture = models.ImageField(null=True, default="avatar.svg")
    connected = models.BooleanField(default=False)
    active = models.BooleanField(default=False)