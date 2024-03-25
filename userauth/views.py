from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserForm, MyUserCreationForm, UserProfileForm
from .models import User, UserProfile, TermsAndConditions, ConnectedAccounts, Facebook, Instagram, Youtube, Linkedin, Google, X, Tiktok
import requests
from socialink.secrets import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET, FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET
from datetime import datetime, timedelta
from django.utils import timezone
import qrcode


def signIn(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
            authenticated_user = authenticate(request, username=username, password=password)
            if authenticated_user is not None:
                login(request, authenticated_user)
                if TermsAndConditions.objects.filter(user=request.user).exists():
                    if ConnectedAccounts.objects.filter(user=request.user, connected=True).exists():
                        return redirect('profile', username=request.user.username)
                    else:
                        return redirect('completeProfile')
                else:
                    return redirect('termsAndconditions')
            else:
                # Error message to be displayed in the template
                messages.error(request, "Invalid username or password")
        except User.DoesNotExist:
            # Error message for non-existent user
            messages.error(request, "User does not exist")

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
            return redirect('termsAndconditions')
        else:
            # Error messages for form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
       
    context = {
        'user_form': user_form,
    }
    return render(request, "userauth/signUp.html", context)


def signOut(request):
    logout(request)
    return redirect('signIn')


def termsAndconditions(request):
    if request.method == 'POST':
        user = request.user
        if not TermsAndConditions.objects.filter(user=user).exists():
            TermsAndConditions.objects.create(
                    user=user,
                    accepted=True,
            )
            return redirect('completeProfile')
    return render(request, "userauth/termsAndconditions.html")


def completeProfile(request):
    if request.method == 'POST':
        connected_accounts = ConnectedAccounts.objects.get(user=request.user)
        connected_accounts.connected = True
        connected_accounts.save()
        return redirect('profile', username=request.user.username)
    
    #user_profile_form = UserProfileForm()
    connected_instagram_account = Instagram.objects.filter(user=request.user)
    connected_facebook_account = Facebook.objects.filter(user=request.user)
    context = {
        #"user_profile_form": user_profile_form,
        "connected_instagram_account": connected_instagram_account,
        "connected_facebook_account": connected_facebook_account,
    }
    return render(request, "userauth/completeProfile.html", context)


def instagramCallback(request):
    # Extract the access code from the query parameters
    code = request.GET.get('code')
    
    # Make a POST request to exchange the access code for an access token
    response = requests.post('https://api.instagram.com/oauth/access_token', data={
        'client_id': INSTAGRAM_CLIENT_ID,
        'client_secret': INSTAGRAM_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': 'https://127.0.0.1:4000/instagram_callback/',
        'code': code,
    })
    
    # Process the response and extract the access token
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        instagram_user_id = data.get('user_id')
        
        if not Instagram.objects.filter(instagram_id=instagram_user_id).exists():
            # Make a GET request to exchange the short-lived access token for a long-lived one
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': INSTAGRAM_CLIENT_SECRET,
                'access_token': access_token,
            }
            ex_change_token = requests.get('https://graph.instagram.com/access_token', params=params)
            
            # Process the exchanged response and extract the long lived access token and expires in date
            if ex_change_token.status_code == 200:
                ex_change_token = ex_change_token.json()
                long_lived_token = ex_change_token.get('access_token')
                long_lived_token_type = ex_change_token.get('token_type')
                long_lived_token_expires_in = ex_change_token.get("expires_in")
                expires_at = timezone.now() + timedelta(seconds=long_lived_token_expires_in)
                
                # Make a GET request to fetch the Instagram username
                api_url = 'https://graph.instagram.com/me'
                params = {
                    'fields': 'username',
                    'access_token': access_token
                }
                instagram_response = requests.get(api_url, params=params)
                if instagram_response.status_code == 200:
                    instagram_data = instagram_response.json()
                    instagram_name = instagram_data.get('username')
                else:
                    messages.error(request, "Error fetching Instagram username")
                
                Instagram.objects.create(
                    user=request.user,
                    instagram_id=instagram_user_id,
                    instagram_name=instagram_name,
                    token=long_lived_token, 
                    token_type=long_lived_token_type,
                    expires=expires_at
                )
                
                # Retrieve or create ConnectedAccounts object for the user
                connected_accounts, created = ConnectedAccounts.objects.get_or_create(user=request.user)
                # Increment the instagram attribute by one
                connected_accounts.instagram += 1
                connected_accounts.save()
                print("SUCCESS")
        else:
            messages.error(request, "Account Already Connected")  
            
    else:
        print("Not Authorized By Instagram")
        
    return redirect('completeProfile')


def facebookCallback(request):
    # Extract the access code from the query parameters
    code = request.GET.get('code')
    
    # Make a POST request to exchange the access code for an access token
    response = requests.post('https://graph.facebook.com/v12.0/oauth/access_token', data={
        'client_id': FACEBOOK_CLIENT_ID,
        'client_secret': FACEBOOK_CLIENT_SECRET,
        'redirect_uri': "https://127.0.0.1:4000/facebook_callback/",
        'code': code,
        'grant_type': 'authorization_code'
    })
    
    # Process the response and extract the access token
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        token_type = data.get('token_type')
        long_lived_token_expires_in = data.get("expires_in")
        expires_at = timezone.now() + timedelta(seconds=long_lived_token_expires_in)
        
        facebook_response = requests.get(f'https://graph.facebook.com/me?fields=id,name&access_token={access_token}')
        # Check if the request was successful
        if facebook_response.status_code == 200:
            user_data = facebook_response.json()
            facebook_user_id = user_data.get('id')
            facebook_user_name = user_data.get('name')
            
            if not Facebook.objects.filter(facebook_id=facebook_user_id).exists():
                Facebook.objects.create(
                        user=request.user,
                        facebook_id=facebook_user_id,
                        facebook_name=facebook_user_name,
                        token=access_token, 
                        token_type=token_type,
                        expires=expires_at
                    )
                
                # Retrieve or create ConnectedAccounts object for the user
                connected_accounts, created = ConnectedAccounts.objects.get_or_create(user=request.user)
                # Increment the facebook attribute by one
                connected_accounts.facebook += 1
                connected_accounts.save()
                print("SUCCESS")
                
            else:
                messages.error(request, "Account Already Connected")
        else:
            print("Error fetching user details:", facebook_response.text)
    else:
        print("Error exchanging code for access token:", response.text)

    return redirect('completeProfile')




def profile(request, username):
    user = User.objects.get(username=request.user)
    user_profile = UserProfile.objects.get(user=user)
    instagram = Instagram.objects.get(user=user)
    
    access_token = instagram.token
    api_url = 'https://graph.instagram.com/me/media'
    params = {
        'fields': 'id,caption,media_type,media_url,thumbnail_url,username,timestamp',
        'access_token': access_token
    }
    instagram_response = requests.get(api_url, params=params)
    if instagram_response.status_code == 200:
        instagram_data = instagram_response.json()
    else:
        error_message = "Error fetching Instagram content"
        
        
        
   

    
    context = {
        "user": user,
        "user_profile": user_profile,
        'instagram_data': instagram_data,
    }
    return render(request, "userauth/profile.html", context)