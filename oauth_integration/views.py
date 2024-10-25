from django.shortcuts import render, redirect, get_object_or_404
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


def instagramAuthorize(request):
    csrf_token = get_token(request)
    # Save the CSRF token in session for later verification
    request.session['instagram_csrf_token'] = csrf_token
    
    # Construct the Instagram authorization URL with the state parameter
    instagram_authorization_url = (
        f"https://www.instagram.com/oauth/authorize/third_party?"
        f"client_id={INSTAGRAM_CLIENT_ID}&"
        f"redirect_uri=https%3A%2F%2F127.0.0.1%3A4000%2Foauth%2Finstagram_callback%2F&"
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
        messages.error(request, "CSRF validation failed")
        return redirect('userauth:completeProfile')

    # Make a POST request to exchange the access code for an access token
    try:
        response = requests.post('https://api.instagram.com/oauth/access_token', data={
            'client_id': INSTAGRAM_CLIENT_ID,
            'client_secret': INSTAGRAM_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://127.0.0.1:4000/oauth/instagram_callback/',
            'code': code,
        })

        # Check if the response is successful
        if response.status_code != 200:
            messages.error(request, "Error exchanging code for access token: {}".format(response.text))
            return redirect('userauth:completeProfile')

        data = response.json()
        access_token = data.get('access_token')
        instagram_user_id = data.get('user_id')

        if not Instagram.objects.filter(instagram_id=instagram_user_id).exists():
            # Exchange the short-lived token for a long-lived one
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': INSTAGRAM_CLIENT_SECRET,
                'access_token': access_token,
            }
            ex_change_token = requests.get('https://graph.instagram.com/access_token', params=params)

            if ex_change_token.status_code != 200:
                messages.error(request, "Error exchanging short-lived token for long-lived token: {}".format(ex_change_token.text))
                return redirect('userauth:completeProfile')

            ex_change_token = ex_change_token.json()
            long_lived_token = ex_change_token.get('access_token')
            long_lived_token_type = ex_change_token.get('token_type')
            long_lived_token_expires_in = ex_change_token.get("expires_in")
            expires_at = timezone.now() + timedelta(seconds=long_lived_token_expires_in)

            # Fetch the Instagram username
            api_url = 'https://graph.instagram.com/me'
            params = {
                'fields': 'username',
                'access_token': long_lived_token
            }
            instagram_response = requests.get(api_url, params=params)

            if instagram_response.status_code != 200:
                messages.error(request, "Error fetching Instagram username: {}".format(instagram_response.text))
                return redirect('userauth:completeProfile')

            instagram_data = instagram_response.json()
            instagram_name = instagram_data.get('username')

            # Create the Instagram object
            Instagram.objects.create(
                user=request.user,
                instagram_id=instagram_user_id,
                instagram_name=instagram_name,
                token=long_lived_token, 
                token_type=long_lived_token_type,
                expires=expires_at
            )

            # Update or create the connected accounts for the user
            connected_accounts, created = ConnectedAccounts.objects.get_or_create(user=request.user)
            connected_accounts.instagram += 1
            connected_accounts.save()

            messages.success(request, "Instagram account successfully connected")
            print("SUCCESS")

        else:
            messages.error(request, "Instagram account is already connected")

    except requests.RequestException as e:
        # General error handling for request exceptions
        messages.error(request, "An error occurred while connecting Instagram: {}".format(str(e)))

    return redirect('userauth:completeProfile')



def facebookAuthorize(request):
    csrf_token = get_token(request)
    # Save the CSRF token in session for later verification
    request.session['facebook_csrf_token'] = csrf_token
    
    # Construct the Facebook authorization URL with the state parameter
    facebook_authorization_url = (
        f"https://www.facebook.com/v6.0/dialog/oauth?"
        f"client_id={FACEBOOK_CLIENT_ID}&"
        f"redirect_uri=https%3A%2F%2F127.0.0.1%3A4000%2Foauth%2Ffacebook_callback%2F&"
        f"state={csrf_token}&"
        f"scope=user_posts,email,user_friends,user_photos,user_likes,user_events,user_birthday,user_location"
    )
    
    return redirect(facebook_authorization_url)


def facebookCallback(request):
    # Extract the access code and state from the query parameters
    code = request.GET.get('code')
    state = request.GET.get('state')

    # Retrieve the CSRF token from session
    csrf_token = request.session.get('facebook_csrf_token')

    # Check if the state parameter matches the CSRF token
    if not constant_time_compare(csrf_token, state):
        messages.error(request, "CSRF validation failed")
        return redirect('userauth:completeProfile')

    # Make a POST request to exchange the access code for an access token
    try:
        response = requests.post('https://graph.facebook.com/v12.0/oauth/access_token', data={
            'client_id': FACEBOOK_CLIENT_ID,
            'client_secret': FACEBOOK_CLIENT_SECRET,
            'redirect_uri': 'https://127.0.0.1:4000/oauth/facebook_callback/',
            'code': code,
            'grant_type': 'authorization_code'
        })

        # Check if the response is successful
        if response.status_code != 200:
            messages.error(request, "Error exchanging Facebook code for access token: {}".format(response.text))
            return redirect('userauth:completeProfile')

        # Process the response and extract the access token
        data = response.json()
        access_token = data.get('access_token')
        long_lived_token_expires_in = data.get("expires_in")
        expires_at = timezone.now() + timedelta(seconds=long_lived_token_expires_in)

        # Fetch the Facebook user ID and name
        try:
            facebook_response = requests.get(f'https://graph.facebook.com/me?fields=id,name&access_token={access_token}')
            if facebook_response.status_code != 200:
                messages.error(request, "Error fetching Facebook user details: {}".format(facebook_response.text))
                return redirect('userauth:completeProfile')

            # Extract user data
            user_data = facebook_response.json()
            facebook_user_id = user_data.get('id')
            facebook_user_name = user_data.get('name')

            # Check if the Facebook account is already connected
            if not Facebook.objects.filter(facebook_id=facebook_user_id).exists():
                # Store the Facebook details in the database
                Facebook.objects.create(
                    user=request.user,
                    facebook_id=facebook_user_id,
                    facebook_name=facebook_user_name,
                    token=access_token,
                    expires=expires_at
                )

                # Retrieve or create ConnectedAccounts object for the user
                connected_accounts, created = ConnectedAccounts.objects.get_or_create(user=request.user)
                connected_accounts.facebook += 1
                connected_accounts.save()

                messages.success(request, "Facebook account connected successfully!")
            else:
                messages.error(request, "Facebook account is already connected.")

        except requests.RequestException as e:
            messages.error(request, "Error occurred while fetching Facebook user details: {}".format(str(e)))
            return redirect('userauth:completeProfile')

    except requests.RequestException as e:
        messages.error(request, "An error occurred during the Facebook authentication process: {}".format(str(e)))
        return redirect('userauth:completeProfile')

    return redirect('userauth:completeProfile')

















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