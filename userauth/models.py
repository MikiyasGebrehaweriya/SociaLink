from django.contrib.auth.models import User
from django.db import models
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=200, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profilePicture = models.ImageField(null=True, default="default_pp.png", blank=True)
    qr_code = models.ImageField(null=True, default="qr_code.png", blank=True)
    user_code = models.CharField(max_length=16, null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Connection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections')
    connected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connected_to')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'connected_user')  # Ensure only one connection between two users

    def __str__(self):
        return f"{self.user.username} connected with {self.connected_user.username}"
    
    
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
    data = models.JSONField(null=True)  # Store JSON data received from Facebook
    last_updated = models.DateTimeField(null=True)  # Track when the data was last updated
    
class Instagram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    instagram_id = models.CharField(max_length=500, null=True)
    instagram_name = models.CharField(max_length=100, null=True)
    token = models.CharField(max_length=500, null=True)
    token_type = models.CharField(max_length=20, null=True)
    expires = models.DateTimeField(null=True)
    lastsync = models.DateTimeField(auto_now=True)
    data = models.JSONField(null=True)  # Store JSON data received from Facebook
    last_updated = models.DateTimeField(null=True)  # Track when the data was last updated
    
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
      
      

class Post(models.Model):
    CONTENT_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content = models.TextField(null=True)  # Stores text content, descriptions, or HTML for embedded media
    media_file = models.FileField(upload_to='posts/media/', blank=True, null=True)  # Optional media
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Define methods to check post types
    def is_image_post(self):
        return self.content_type == 'image'

    def is_video_post(self):
        return self.content_type == 'video'

    def is_text_post(self):
        return self.content_type == 'text'

    # Add additional methods or fields as needed

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"


