from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm, MyUserCreationForm, UserProfileForm
from .models import User, UserProfile

# Create your views here.
def signIn(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        print(username, password)
        print(request)

        try:
            get_user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('signIn')
            else:
                print("INCORRECT")
                
        except Exception as e:
            print("NO USER")
   
    context = {}
    return render(request, "userauth/signIn.html", context)


def signUp(request):
    user_form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('completeProfile')
        else:
            print("INCORRECT")
       
    context = {
        'user_form': user_form,
    }
    return render(request, "userauth/signUp.html", context)


def completeProfile(request):
    user_profile_form = UserProfileForm()
    context = {
        "user_profile_form": user_profile_form,
    }
    return render(request, "userauth/completeProfile.html", context)