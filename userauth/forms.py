from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profilePicture', 'fullName', 'bio']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

