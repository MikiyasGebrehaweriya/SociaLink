"""
The Python script contains functions for user authentication, profile management, social media
account connections, generating QR codes, handling CSRF tokens, and interacting with external APIs.
:return: The code snippet provided contains various functions related to user authentication,
profile management, social media account connections, and posting functionalities in a Django
project. The functions handle user sign-in, sign-up, sign-out, terms and conditions acceptance,
profile completion, social media account authorization callbacks, profile viewing, AI interaction,
member listing, post creation, profile updates, connections between users, reporting CSP violations,
post deletion
"""

# The above code is a Python script that imports various modules and classes from the Django
# framework. It includes functionalities for rendering views, handling HTTP responses, managing CSRF
# tokens, working with forms, models, authentication, and settings in a Django project.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.middleware.csrf import constant_time_compare
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings

from .forms import UserForm, MyUserCreationForm, UserProfileForm
from .models import User, UserProfile, TermsAndConditions, ConnectedAccounts, Facebook, Instagram, Youtube, Linkedin, Google, X, Tiktok, Post, Connection
import requests
from socialink.secrets import INSTAGRAM_CLIENT_ID, INSTAGRAM_CLIENT_SECRET, FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET
from datetime import datetime, timedelta
from django.utils import timezone
import qrcode
import psycopg2
import json
import os
import random


import langchain.agents
import langchain_community.agent_toolkits
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
import os

load_dotenv()


# load_dotenv()
# API_KEY = os.environ.get("OPENAI_API_KEY")

def generate_unique_number():
    while True:
        # Generate a random 16-digit number
        random_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        
        # Check if the number already exists in the database
        if not UserProfile.objects.filter(user_code=random_number).exists():
            return random_number


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
    return render(request, "userauth/signIn2.html", context)


def signUp(request):
    user_form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            
            # Generate QR code content (e.g., user profile URL)
            qr_content = request.build_absolute_uri(f'/profile/{user.username}/')
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#135D66", back_color="#FFF5E0")
            
            # Save the QR code image to the media root's "qrcodes" folder
            media_root = settings.MEDIA_ROOT
            qrcodes_folder = os.path.join(media_root, 'qrcodes')
            if not os.path.exists(qrcodes_folder):
                os.makedirs(qrcodes_folder)
            qr_img_path = os.path.join(qrcodes_folder, f'{user.username}_qr.png')
            qr_img.save(qr_img_path)
            
            unique_number = generate_unique_number()
            print(unique_number)
            
            # Create a UserProfile object for the user and save the QR code path
            user_profile = UserProfile.objects.create(user=user)
            user_profile.qr_code = qr_img_path
            user_profile.user_code = unique_number
            user_profile.save()
            
            return redirect('termsAndconditions')
        else:
            # Error messages for form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
       
    context = {
        'user_form': user_form,
    }
    return render(request, "userauth/signUp2.html", context)


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
    return render(request, "userauth/completeProfile2.html", context)


def instagramAuthorize(request):
    csrf_token = get_token(request)
    # Save the CSRF token in session for later verification
    request.session['instagram_csrf_token'] = csrf_token
    
    # Construct the Instagram authorization URL with the state parameter
    instagram_authorization_url = (
        f"https://www.instagram.com/oauth/authorize/third_party?"
        f"client_id={INSTAGRAM_CLIENT_ID}&"
        f"redirect_uri=https%3A%2F%2F127.0.0.1%3A4000%2Finstagram_callback%2F&"
        f"scope=user_profile%2Cuser_media&"
        f"response_type=code&"
        f"logger_id=1f889917-cda8-490e-9e7d-6b3ee7e51de2&"
        f"state={csrf_token}"
    )
    return redirect(instagram_authorization_url)


def instagramCallback(request):
    # Extract the access code and state from the query parameters
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # Retrieve the CSRF token from session
    csrf_token = request.session.get('instagram_csrf_token')

    # Check if the state parameter matches the CSRF token
    if not constant_time_compare(csrf_token, state):
        # Handle CSRF validation failure
        # Error message to be displayed in the template
        messages.error(request, "CSRF validation failed")
        return redirect('completeProfile')
    
    
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
            print(user_data)
            facebook_user_id = user_data.get('id')
            facebook_user_name = user_data.get('name')
            
            if Facebook.objects.filter(facebook_id=facebook_user_id).exists():
                messages.error(request, "Account Already Connected")
            else:
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
            print("Error fetching user details:", facebook_response.text)
    else:
        print("Error exchanging code for access token:", response.text)

    return redirect('completeProfile')


def youtubeCallback(request):
    pass

def linkedinCallback(request):
    pass

def xCallback(request):
    pass

def snapchatCallback(request):
    pass

def tiktokCallback(request):
    pass

def googleCallback(request):
    pass   

def twitchCallback(request):
    pass    

def githubCallback(request):
    pass

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    logged_user_profile = UserProfile.objects.get(user=request.user)
    is_own_profile = request.user.is_authenticated and str(request.user) == str(profile.username)
    print(is_own_profile, profile, profile.username, request.user, request.user.is_authenticated)
    
    user = User.objects.get(username=username)
    user_profile = UserProfile.objects.get(user=user)
    list_of_users_profile = UserProfile.objects.exclude(user=user).order_by('-created_at')[:5]
    profile_form = UserProfileForm(instance=request.user)
    instagram = Instagram.objects.get(user=user)
    facebook = Facebook.objects.get(user=user)
    
    posts = Post.objects.filter(user=user).order_by('-created_at')
    
    # Retrieve the connected users for the current user
    connected_users = Connection.objects.filter(user=user).values_list('connected_user', flat=True)
    # Retrieve the 5 most recent posts from the connected users
    recent_posts_form_connected_users = Post.objects.filter(user__in=connected_users).order_by('-created_at')[:4]
    
    
    connected_instagram_account = Instagram.objects.filter(user=user)
    connected_facebook_account = Facebook.objects.filter(user=user)
    # Retrieve the ConnectedAccounts object for the user
    user_connected_account = ConnectedAccounts.objects.get(user=user)
    # Sum up the values of all attributes
    total_connected = (
        user_connected_account.facebook +
        user_connected_account.instagram +
        user_connected_account.youtube +
        user_connected_account.linkedin +
        user_connected_account.google +
        user_connected_account.x +
        user_connected_account.tiktok
    )
    
    
    instagram_access_token = instagram.token
    api_url = 'https://graph.instagram.com/me/media'
    params = {
        'fields': 'id,caption,media_type,media_url,thumbnail_url,username,timestamp',
        'access_token': instagram_access_token
    }
    instagram_response = requests.get(api_url, params=params)
    if instagram_response.status_code == 200:
        instagram_data = instagram_response.json()
        instagram_user = Instagram.objects.get(user=user)
        instagram_user.data = instagram_data
        instagram_user.last_updated = timezone.now()
        instagram_user.save()
    else:
        error_message = "Error fetching Instagram content"
        print(error_message)
        
        
    facebook_access_token = facebook.token
    api_url = 'https://graph.facebook.com/v12.0/me'
    params = {
        'fields': 'name,email,birthday,photos,posts,likes,events,hometown,friends',
        'access_token': facebook_access_token
    }    
    facebook_response = requests.get(api_url, params=params)
    if facebook_response.status_code == 200:
        facebook_data = facebook_response.json()
        facebook_user = Facebook.objects.get(user=user)
        facebook_user.data = facebook_data
        facebook_user.last_updated = timezone.now()
        facebook_user.save()
    else:    
        error_message = "Error fetching Facebook content"
        print(error_message)

    
    context = {
        "user": user,
        "user_profile": user_profile,
        "logged_user_profile": logged_user_profile,
        "profile_form": profile_form,
        'instagram_data': instagram_data,
        "total_connected": total_connected,
        "connected_instagram_account": connected_instagram_account,
        "connected_facebook_account": connected_facebook_account,
        "is_own_profile": is_own_profile,
        "posts": posts,
        "recent_posts_form_connected_users": recent_posts_form_connected_users,
        "list_of_users_profile": list_of_users_profile,
    }
    return render(request, "userauth/members-page.html", context)


# Database and OpenAI API details from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_db_connection():
    """
    Returns an instance of the SQLDatabase from the database URI.
    """
    try:
        db = SQLDatabase.from_uri(DATABASE_URL)
        return db
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    
    
def get_llm():
    """
    Returns an instance of the OpenAI language model with predefined settings.
    """
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.5,  # Lower temperature for more deterministic results
            api_key=OPENAI_API_KEY
        )
        return llm
    except Exception as e:
        print(f"Error initializing OpenAI: {e}")
        return None

def get_user_profile(user):
    """
    Fetches the user's profile and relevant social media data, incorporating data from both the User model and UserProfile model.
    """
    try:
        # Get the UserProfile linked to the user
        user_account = User.objects.get(username=user)
        user_profile = UserProfile.objects.get(user=user)
        
        # Get social media data associated with the user
        instagram_data = Instagram.objects.filter(user=user)
        facebook_data = Facebook.objects.filter(user=user)
        youtube_data = Youtube.objects.filter(user=user)
        linkedin_data = Linkedin.objects.filter(user=user)
        google_data = Google.objects.filter(user=user)
        x_data = X.objects.filter(user=user)
        tiktok_data = Tiktok.objects.filter(user=user)

        # Combine all user data into a comprehensive dictionary
        user_data = {
            'profile': {
                'username': user_account.username,
                'email': user_account.email,
                'date_joined': user_account.date_joined,
                'last_login': user_account.last_login,
                'full_name': user_profile.fullName,
                'bio': user_profile.bio,
                'profile_picture': user_profile.profilePicture.url if user_profile.profilePicture else None,
                'qr_code': user_profile.qr_code.url if user_profile.qr_code else None,
                'user_code': user_profile.user_code,
                'verified': user_profile.verified,
                'created_at': user_profile.created_at,
            },
            'social_media': {
                'instagram': list(instagram_data.values()),
                'facebook': list(facebook_data.values()),
                'youtube': list(youtube_data.values()),
                'linkedin': list(linkedin_data.values()),
                'google': list(google_data.values()),
                'x': list(x_data.values()),
                'tiktok': list(tiktok_data.values()),
            }
        }
        return user_data

    except UserProfile.DoesNotExist:
        return None


def construct_schema_prompt():
    """
    Constructs a prompt that makes the AI aware of the entire database schema,
    covering tables related to users and multiple social media platforms.
    This helps generate accurate SQL queries for various data sources.
    """
    schema_description = (
        "The database schema consists of the following tables:\n"
        "- User: Contains 'id', 'username', 'email', 'password', 'last_login', and 'date_joined' and more. This table stores core user account information.\n"
        "- UserProfile: Linked to the User table via a one-to-one relationship, with fields such as 'user_id', 'fullName', 'bio', 'profilePicture', 'qr_code', 'user_code', 'verified', and 'created_at'.\n"
        "- Instagram: Stores social media data for Instagram, with fields 'user_id', 'user', 'instagram name',  'data', 'lasted updated', .\n"
        "- Facebook: Stores social media data for Facebook, with fields 'user_id', 'user', 'facebook name',  'data', 'lasted updated' .\n"
        "- YouTube: Contains 'user_id', 'video_title', 'video_link', 'views'.\n"
        "- LinkedIn: Stores LinkedIn data, including 'user_id', 'position', 'company', 'years_of_experience'.\n"
        "- Google: Contains 'user_id', 'search_query', 'search_results'.\n"
        "- X (formerly Twitter): Contains 'user_id', 'tweet', 'retweets', 'likes'.\n"
        "- TikTok: Contains 'user_id', 'video_title', 'likes', 'comments'.\n\n"
        "Use this schema to retrieve data from the relevant sources when querying for any information, ensuring that relationships between User and UserProfile, as well as User and social media data, are properly respected."
    )
    return schema_description



def construct_user_query_prompt(user_data, user_query):
    """
    Constructs a prompt that includes the user's profile context, their query, and data from all connected platforms.
    """
    schema_prompt = construct_schema_prompt()
    
    # User profile context: Combines data from both User and UserProfile
    profile_info = (
        f"The current user is {user_data['profile'].get('username', 'Unknown')} ({user_data['profile'].get('email', 'No email available')}). "
        f"Their username is {user_data['profile'].get('username', 'No username')}, and they joined the platform on {user_data['profile'].get('date_joined', 'Unknown')}. "
        f"Last login was on {user_data['profile'].get('last_login', 'Unknown')}."
    )
    
    # Social media platforms the user is connected to
    platforms = []
    if user_data['social_media']['instagram']:
        platforms.append("Instagram")
    if user_data['social_media']['facebook']:
        platforms.append("Facebook")
    if user_data['social_media']['youtube']:
        platforms.append("YouTube")
    if user_data['social_media']['linkedin']:
        platforms.append("LinkedIn")
    if user_data['social_media']['google']:
        platforms.append("Google")
    if user_data['social_media']['x']:
        platforms.append("X")
    if user_data['social_media']['tiktok']:
        platforms.append("TikTok")

    connected_platforms = ", ".join(platforms) if platforms else "no connected platforms."

    # Constructing the full prompt
    return (
        f"The current user is {user_data['profile'].get('username', 'Unknown')} ({user_data['profile'].get('email', 'No email available')}). "
        f"The user's complete profile info: {profile_info}. They are connected to the following platforms: {connected_platforms}. "
        f"The user has asked the following query: '{user_query}'. "
        f"Use data from all relevant tables like User, UserProfile, and social media accounts (Instagram, Facebook, YouTube, LinkedIn, Google, X, TikTok) to generate an accurate response. "
        f"Use the retrived data and provide a detailed, human-readable summary of the data instead of simply confirming retrieval. "
        f"Ensure the query is answered in a clear, concise, and easy-to-read format. "
        f"The database schema is as follows: {schema_prompt}."
    )



def run_agent(db, llm, question):
    """
    Executes the LangChain SQL agent and handles errors gracefully.
    """
    try:
        # Create the SQL agent using the LLM and the database connection
        agent = create_sql_agent(llm, db=db, verbose=True)
        
        # Run the question through the agent
        answer = agent.run(question)
        return answer
    except Exception as e:
        print(f"Error running the agent: {e}")
        return "There was an issue processing your request. Please try again later."


def ai(request):
    """
    AI view that handles user queries, utilizing their profile context.
    """
    if request.method == 'POST':
        user_query = request.POST.get('data')
        
        if not user_query:
            return JsonResponse({'error': 'No query provided'}, status=400)
        
        # Fetch the current user's profile and social data
        user_data = get_user_profile(request.user)
        
        if not user_data:
            return JsonResponse({'error': 'User profile not found'}, status=404)

        # Set up database connection and language model
        db = get_db_connection()
        llm = get_llm()
        
        if not db or not llm:
            return JsonResponse({'error': 'Unable to process request due to configuration error'}, status=500)

        # Construct the prompt with user context and schema knowledge
        prompt = construct_user_query_prompt(user_data, user_query)
        
        # Run the agent and get the response
        answer = run_agent(db, llm, prompt)

        response_data = {'message': answer}
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)







# def ai(request):
#     if request.method == 'POST':
#         data = request.POST.get('data')
#         instagram_json = Instagram.objects.get(user=request.user).data
        
#         # db_user = "TestUser"
#         # db_password = "testuserpassword"
#         # db_host = "localhost"
#         # db_port = "5432"
#         # db_name = "SociaLink"
#         # db = SQLDatabase.from_uri(f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
#         db = SQLDatabase.from_uri(f"postgresql://postgres:ozsodeRWiakLaNGJWQaHqYTESHtmXwNm@junction.proxy.rlwy.net:52888/railway") 
        
        
#         # Configure your OpenAI API key
#         OPENAI_API_KEY = "your_openai_api_key"
#         llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key="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")

       
#         agent = create_sql_agent(llm, db=db, verbose=True)
#         question = str(data)
#         answer = agent.run(question)


#         response_data = {'message': answer}
#         return JsonResponse(response_data)
#     return JsonResponse({'error': 'Invalid request method'})


def members(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query')
        search_query = (
            Q(user__username__icontains=search_query) |  # Search in the username field of the related User model
            Q(fullName__icontains=search_query) |       # Search in the fullName field of UserProfile
            Q(user__email__icontains=search_query) |    # Search in the email field of the related User model
            Q(user_code__icontains=search_query)       # Search in the user_code field of UserProfile
        )
        users_profile = UserProfile.objects.filter(search_query).exclude(user=request.user)
    else:
        users_profile = UserProfile.objects.all().exclude(user=request.user)
        
    logged_user_profile = UserProfile.objects.get(user=request.user)
    connections = Connection.objects.filter(user=request.user)
    connected_users = Connection.objects.filter(user=request.user).values_list('connected_user', flat=True)
    context = {
        "users_profile": users_profile,
        "logged_user_profile": logged_user_profile,
        "connections": connections,
        "connected_users": connected_users,
    }
    return render(request, "userauth/members2.html", context)


def create(request):        
    user = request.user
    user_profile = UserProfile.objects.get(user=request.user)
    total_posts = Post.objects.filter(user=user).count()
    image_posts = Post.objects.filter(user=user, content_type="image").count()
    video_posts = Post.objects.filter(user=user, content_type="video").count()
    twitte_posts = Post.objects.filter(user=user, content_type="text").count()
    recent_posts = Post.objects.filter(user=user).order_by('-created_at')[:5]
    latest_post = Post.objects.filter(user=user).latest('created_at')
    top5_recent_posts = Post.objects.filter(user=user).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        if 'twitte_submit' in request.POST:
            twitte = request.POST.get('twitte')
            post = Post.objects.create(user=user, content_type='text', content=twitte)
            print("Twitte submitted: " + twitte)
        elif 'image_submit' in request.POST:
            image = request.FILES.get('image') 
            caption = request.POST.get('caption') 
            post = Post.objects.create(user=user, content_type="image", media_file=image, content=caption)
            print("Image submitted", image)
        elif 'video_submit' in request.POST:
            video = request.FILES.get('video') 
            caption = request.POST.get('caption')
            post = Post.objects.create(user=user, content_type="video", media_file=video, content=caption)
            print("Video submitted", video)
                     
    context = {
        "user_profile": user_profile,
        "total_posts": total_posts,
        "twitte_posts": twitte_posts,
        "image_posts": image_posts,
        "video_posts": video_posts,
        "recent_posts": recent_posts,
        "latest_post": latest_post,
    }
    
    return render(request, "userauth/create.html", context)



def update_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    
    return redirect('profile', username=request.user.username)


def connect(request, username):
    user = request.user
    connected_user = User.objects.get(username=username)
    check_connection = Connection.objects.filter(user=user, connected_user=connected_user).exists()
    if check_connection:
        messages.error(request, "Connection already exists")
    else:
        connect_user = Connection.objects.create(user=user, connected_user=connected_user)
    return redirect('profile', username=username)


def report_csp_violation(request):
    if request.method == 'POST':
        # Process the CSP violation report data (JSON)
        report_data = json.loads(request.body)
        # Log the report data for analysis
        # ... (Your logging implementation here)
        return HttpResponse(status=204)  # No Content response
    return HttpResponseBadRequest()


def delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect('profile', username=request.user.username)

def update(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        if 'twitte_submit' in request.POST:
            twitte = request.POST.get('twitte')
            post.content = twitte
            post.save()
        elif 'image_submit' in request.POST:
            caption = request.POST.get('caption')
            post.content = caption
            post.save()
        elif 'video_submit' in request.POST: 
            caption = request.POST.get('caption')
            post.content = caption
            post.save()
        return redirect('profile', username=request.user.username)
    context = {
        "post": post
    }
    return render(request, "userauth/update.html", context)