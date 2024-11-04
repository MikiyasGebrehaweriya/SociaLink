from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.middleware.csrf import constant_time_compare
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings

from userauth.forms import UserForm, MyUserCreationForm, UserProfileForm
from userauth.models import User, UserProfile, TermsAndConditions, ConnectedAccounts, Facebook, Instagram, Youtube, Linkedin, Google, X, Tiktok, Post, Connection
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
# Database and OpenAI API details from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")




# Helper function to handle Instagram data fetching

def fetch_instagram_data(instagram_token):
    api_url = 'https://graph.instagram.com/me/media'
    params = {
        'fields': 'id,caption,media_type,media_url,thumbnail_url,username,timestamp',
        'access_token': instagram_token
    }
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching Instagram content: {response.status_code}")
        return None


# Helper function to handle Facebook data fetching

def fetch_facebook_data(facebook_token):
    api_url = 'https://graph.facebook.com/v12.0/me'
    params = {
        'fields': 'name,email,birthday,photos,posts,likes,events,hometown,friends',
        'access_token': facebook_token
    }
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching Facebook content: {response.status_code}")
        return None


# Main profile view

def profile(request, username):
    # Fetch user and profile details
    profile = get_object_or_404(User, username=username)
    logged_user_profile = UserProfile.objects.get(user=request.user)
    is_own_profile = request.user.is_authenticated and request.user.username == profile.username

    try:
        user_profile = UserProfile.objects.get(user=profile)
        instagram_account = Instagram.objects.get(user=profile)
        facebook_account = Facebook.objects.get(user=profile)
    except ObjectDoesNotExist:
        user_profile, instagram_account, facebook_account = None, None, None

    # Fetch posts related to the user
    posts = Post.objects.filter(user=profile).order_by('-created_at')
    
    # Fetch connected users and their recent posts
    connected_users = Connection.objects.filter(user=profile).values_list('connected_user', flat=True)
    recent_posts_from_connected_users = Post.objects.filter(user__in=connected_users).order_by('-created_at')[:4]
    
    # Fetch the 5 most recent user profiles excluding the current user
    recent_profiles = UserProfile.objects.exclude(user=profile).order_by('-created_at')[:5]

    # Fetch or initialize the profile form
    profile_form = UserProfileForm(instance=request.user)

    # Handle Instagram data
    instagram_data = None
    if instagram_account:
        instagram_data = fetch_instagram_data(instagram_account.token)
        if instagram_data:
            instagram_account.data = instagram_data
            instagram_account.last_updated = timezone.now()
            instagram_account.save()

    # Handle Facebook data
    facebook_data = None
    if facebook_account:
        facebook_data = fetch_facebook_data(facebook_account.token)
        if facebook_data:
            facebook_account.data = facebook_data
            facebook_account.last_updated = timezone.now()
            facebook_account.save()

    # Calculate the total connected accounts
    try:
        user_connected_account = ConnectedAccounts.objects.get(user=profile)
        total_connected = sum([
            user_connected_account.facebook,
            user_connected_account.instagram,
            user_connected_account.youtube,
            user_connected_account.linkedin,
            user_connected_account.google,
            user_connected_account.x,
            user_connected_account.tiktok
        ])
    except ConnectedAccounts.DoesNotExist:
        total_connected = 0  # Default to 0 if no connected accounts are found

    connected_instagram_account = Instagram.objects.filter(user=profile)
    connected_facebook_account = Facebook.objects.filter(user=profile)
    
    # Context data to pass to the template
    context = {
        "user": profile,
        "user_profile": user_profile,
        "logged_user_profile": logged_user_profile,
        "profile_form": profile_form,
        "instagram_data": instagram_data,
        "facebook_data": facebook_data,
        "total_connected": total_connected,
        "is_own_profile": is_own_profile,
        "posts": posts,
        "recent_posts_from_connected_users": recent_posts_from_connected_users,
        "recent_profiles": recent_profiles,
        "connected_instagram_account": connected_instagram_account,
        "connected_facebook_account": connected_facebook_account,
    }

    return render(request, "userauth/members-page.html", context)


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
    Constructs a detailed schema prompt that provides the AI with comprehensive knowledge 
    of the entire database structure, ensuring proper query generation for data retrieval 
    across various tables, including users, profiles, and connected social media platforms.
    """
    schema_description = (
        "The database schema consists of the following tables:\n"
        "- User: This table stores core user account information, with fields such as 'id', 'username', 'email', "
        "'password', 'last_login', 'date_joined', and more.\n"
        "- UserProfile: Linked to the User table via a one-to-one relationship, this table stores user profile details, "
        "including 'user_id', 'fullName', 'bio', 'profilePicture', 'qr_code', 'user_code', 'verified', and 'created_at'.\n"
        "- Connection: This table tracks user connections, linking 'user' and 'connected_user' (both references to the User table), "
        "with a unique constraint to prevent duplicate connections.\n"
        "- TermsAndConditions: Contains 'user_id' and 'accepted' status, tracking whether a user has accepted the platform's terms.\n"
        "- Instagram: Stores Instagram social media data, with fields such as 'user_id', 'instagram_id', 'instagram_name', 'token', "
        "'token_type', 'expires', 'lastsync', 'data', and 'last_updated'.\n"
        "- Facebook: Stores Facebook social media data with similar fields as Instagram: 'user_id', 'facebook_id', 'facebook_name', "
        "'token', 'token_type', 'expires', 'lastsync', 'data', and 'last_updated'.\n"
        "- YouTube: Stores YouTube-related data with 'user_id', 'token', 'token_type', 'expires', and 'lastsync'.\n"
        "- LinkedIn: Stores LinkedIn social media data with 'user_id', 'token', 'token_type', 'expires', and 'lastsync'.\n"
        "- Google: Stores Google-related data with 'user_id', 'token', 'token_type', 'expires', and 'lastsync'.\n"
        "- X (formerly Twitter): Stores X (Twitter) social media data with 'user_id', 'token', 'token_type', 'expires', and 'lastsync'.\n"
        "- TikTok: Stores TikTok data with 'user_id', 'token', 'token_type', 'expires', and 'lastsync'.\n"
        "- ConnectedAccounts: Tracks if a user has connected their accounts to the platform, with fields such as 'connected', 'facebook', "
        "'instagram', 'youtube', 'linkedin', 'google', 'x', and 'tiktok'.\n"
        "- Post: This table stores user-generated content, with fields 'user_id', 'content_type', 'content', 'media_file', 'created_at', and 'updated_at'.\n\n"
        "This schema is designed to track users' core information, their social media connections, and content they share. Use these relationships "
        "to ensure that SQL queries accurately reflect the structure and purpose of the database, respecting relationships like one-to-one and foreign key constraints."
    )
    return schema_description


def construct_user_query_prompt(user_data, user_query):
    """
    Constructs a detailed prompt for the AI, incorporating the user's profile, social media connections,
    and their query, to generate precise SQL queries for the agent.
    """
    schema_prompt = construct_schema_prompt()

    # User profile context: Combines data from both User and UserProfile
    profile_info = (
        f"The current user is {user_data['profile'].get('username', 'Unknown')} (email: {user_data['profile'].get('email', 'No email available')}). "
        f"They joined the platform on {user_data['profile'].get('date_joined', 'Unknown')} and last logged in on {user_data['profile'].get('last_login', 'Unknown')}. "
        f"Their profile includes the full name: {user_data['profile'].get('fullName', 'No full name')}, bio: {user_data['profile'].get('bio', 'No bio')}, "
        f"and verification status: {'Verified' if user_data['profile'].get('verified') else 'Not Verified'}."
    )

    # Social media platforms the user is connected to
    platforms = []
    if user_data['social_media'].get('instagram'):
        platforms.append("Instagram")
    if user_data['social_media'].get('facebook'):
        platforms.append("Facebook")
    if user_data['social_media'].get('youtube'):
        platforms.append("YouTube")
    if user_data['social_media'].get('linkedin'):
        platforms.append("LinkedIn")
    if user_data['social_media'].get('google'):
        platforms.append("Google")
    if user_data['social_media'].get('x'):
        platforms.append("X")
    if user_data['social_media'].get('tiktok'):
        platforms.append("TikTok")

    connected_platforms = ", ".join(platforms) if platforms else "no connected platforms."

    # Constructing the full prompt
    prompt = (
        f"The current user is {user_data['profile'].get('username', 'Unknown')} (email: {user_data['profile'].get('email', 'No email available')}). "
        f"The user has the following profile information: {profile_info}. They are connected to the following platforms: {connected_platforms}. "
        f"The user has asked the following query: '{user_query}'. "
        f"Use data from the relevant tables, including User, UserProfile, and connected social media accounts like Instagram, Facebook, YouTube, LinkedIn, "
        f"Google, X, and TikTok, to generate an accurate response. "
        f"Ensure that relationships between tables (e.g., User to UserProfile, User to social media tables) are respected in your queries. "
        f"Retrieve relevant data and provide a detailed, human-readable summary, ensuring clarity and completeness in the response. "
        f"The database schema is as follows: {schema_prompt}."
    )

    return prompt


def run_agent(db, llm, question):
    """
    Executes the LangChain SQL agent and handles errors gracefully.
    """
    try:
        # Create the SQL agent using the LLM and the database connection
        agent = create_sql_agent(llm, db=db, verbose=True)
        
        # Run the question through the agent
        answer = agent.invoke(question, handle_parsing_errors=True)
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
        print(answer)

        response_data = {'message': answer["output"]}
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)



# Helper function for searching user profiles

def search_user_profiles(search_query, logged_user):
    search_filter = (
        Q(user__username__icontains=search_query) |  # Search by username
        Q(fullName__icontains=search_query) |        # Search by full name
        Q(user__email__icontains=search_query) |     # Search by email
        Q(user_code__icontains=search_query)         # Search by user code
    )
    return UserProfile.objects.filter(search_filter).exclude(user=logged_user)


# Main members view function

def members(request):
    users_profile = None  # Default value for profiles

    # Handle the POST request with search functionality
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '').strip()  # Get search query and strip whitespace
        if search_query:  # Only perform the search if query is non-empty
            users_profile = search_user_profiles(search_query, request.user)
        else:
            users_profile = UserProfile.objects.none()  # No search query, return empty queryset
    else:
        # Fetch all users excluding the logged-in user for GET request
        users_profile = UserProfile.objects.all().exclude(user=request.user)

    try:
        # Get the logged-in user's profile
        logged_user_profile = UserProfile.objects.select_related('user').get(user=request.user)

        # Fetch connections for the logged-in user
        connections = Connection.objects.filter(user=request.user)

        # Get the connected users (only their IDs for efficiency)
        connected_users = connections.values_list('connected_user', flat=True)
    except ObjectDoesNotExist:
        # Handle cases where the user profile does not exist
        logged_user_profile = None
        connections = None
        connected_users = None
        # Optionally, add a log or message to inform the user or the dev team

    # Context data to pass to the template
    context = {
        "users_profile": users_profile,
        "logged_user_profile": logged_user_profile,
        "connections": connections,
        "connected_users": connected_users,
    }

    # Render the members page with the given context
    return render(request, "userauth/members2.html", context)


 # Ensure only authenticated users can access this view
def update_profile(request):
    try:
        # Fetch the user profile or create a new one if it doesn't exist
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    except UserProfile.DoesNotExist:
        # Handle the case where the user profile cannot be created
        messages.error(request, "Unable to fetch or create your profile. Please try again.")
        return redirect('profile_management:profile', username=request.user.username)

    if request.method == 'POST':
        # Handle form submission, including files
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile_management:profile', username=request.user.username)
        else:
            # Display validation errors to the user
            messages.error(request, "There was an error updating your profile. Please check the form and try again.")
    else:
        # Display an empty form for GET requests
        form = UserProfileForm(instance=user_profile)

    # Render the profile update form
    return render(request, 'userauth/update_profile.html', {'form': form})


def connect(request, username):
    user = request.user
    
    # Ensure the connected user exists, otherwise return 404
    connected_user = get_object_or_404(User, username=username)

    # Prevent users from connecting to themselves
    if user == connected_user:
        messages.error(request, "You cannot connect to yourself.")
        return redirect('profile_management:profile', username=username)

    # Check if the connection already exists
    if Connection.objects.filter(user=user, connected_user=connected_user).exists():
        messages.error(request, "Connection already exists.")
    else:
        # Create the connection if it does not exist
        Connection.objects.create(user=user, connected_user=connected_user)
        messages.success(request, f"You are now connected with {connected_user.username}.")

    # Redirect back to the connected user's profile page
    return redirect('profile_management:profile', username=username)


def ai_chat(request):
    return render(request, "profile_management/ai_chat2.html")



