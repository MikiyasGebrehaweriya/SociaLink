from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=200, null=True)
    bio = models.TextField(null=True)
    profilePicture = models.ImageField(null=True, default="avatar.svg")
    qr_code = models.ImageField(null=True, default="qr_code.png")
    
class TermsAndConditions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    date_accepted = models.DateTimeField(auto_now_add=True)

class Facebook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    facebook_id = models.CharField(max_length=500, null=True)
    facebook_name = models.CharField(max_length=100, null=True)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class Instagram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instagram_id = models.CharField(max_length=500, null=True)
    instagram_name = models.CharField(max_length=100, null=True)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class Youtube(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class Linkedin(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class Google(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class X(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class Tiktok(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    
class ConnectedAccounts(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    connected = models.BooleanField(default=False)
    facebook = models.IntegerField(default=0)
    instagram = models.IntegerField(default=0)
    youtube = models.IntegerField(default=0)
    linkedin = models.IntegerField(default=0)
    google = models.IntegerField(default=0)
    x = models.IntegerField(default=0)
    tiktok = models.IntegerField(default=0)
      