"""
User Authentication Views for the userauth app.
Includes functions for user sign-in, sign-up, sign-out, terms and conditions acceptance,
and profile completion.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .forms import MyUserCreationForm
from .models import User, UserProfile, TermsAndConditions, ConnectedAccounts, Facebook, Instagram
import os
import qrcode
import random
import json

from dotenv import load_dotenv
load_dotenv()

# Constants
QR_BOX_SIZE = 10
QR_BORDER_SIZE = 4
QR_FILL_COLOR = "#135D66"
QR_BACK_COLOR = "#FFF5E0"


def generate_unique_number():
    """
    Generate a unique 16-digit code that does not already exist in the UserProfile model.

    This function continuously generates random 16-digit numbers until it finds one
    that is not already used in the `user_code` field of any `UserProfile` instance.

    Returns:
        str: A unique 16-digit string that can be used as a user code.
    """
    while True:
        random_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        if not UserProfile.objects.filter(user_code=random_number).exists():
            return random_number


def generate_qr_code(content, username):
    """
    Generate and save a QR code image for the given content.

    This function creates a QR code from the provided content and saves it as an image file.
    The image is saved in a 'qrcodes' directory within the media root, with the filename
    format '{username}_qr.png'.

    Args:
        content (str): The data to encode in the QR code.
        username (str): The username used to name the QR code image file.

    Returns:
        str: The file path to the saved QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER_SIZE,
    )
    qr.add_data(content)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=QR_FILL_COLOR, back_color=QR_BACK_COLOR)

    media_root = settings.MEDIA_ROOT
    qrcodes_folder = os.path.join(media_root, 'qrcodes')
    if not os.path.exists(qrcodes_folder):
        os.makedirs(qrcodes_folder)
    qr_img_path = os.path.join(qrcodes_folder, f'{username}_qr.png')
    qr_img.save(qr_img_path)

    return qr_img_path


def sign_in(request):
    """Handle user sign-in by authenticating credentials and redirecting appropriately."""
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            terms_exists = TermsAndConditions.objects.filter(user=request.user).exists()
            connected_accounts_exists = ConnectedAccounts.objects.filter(user=request.user, connected=True).exists()
            
            if terms_exists:
                return redirect('profile_management:profile', username=request.user.username) if connected_accounts_exists else redirect('userauth:completeProfile')
            return redirect('userauth:termsAndconditions')
        messages.error(request, "Invalid username or password")
    
    return render(request, "userauth/signIn2.html")


def sign_up(request):
    """Handle new user registration, save QR code, and redirect to terms acceptance."""
    user_form = MyUserCreationForm(request.POST or None)
    
    if user_form.is_valid():
        user = user_form.save(commit=False)
        user.username = user.username.lower()
        user.save()
        login(request, user)

        qr_content = request.build_absolute_uri(f'/profile/{user.username}/')
        qr_img_path = generate_qr_code(qr_content, user.username)
        unique_number = generate_unique_number()
        
        UserProfile.objects.create(
            user=user,
            qr_code=qr_img_path,
            user_code=unique_number
        )
        
        return redirect('userauth:termsAndconditions')
    
    for field, errors in user_form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    
    return render(request, "userauth/signUp2.html", {'user_form': user_form})


def sign_out(request):
    """Log out the current user and redirect to sign-in page."""
    logout(request)
    return redirect('userauth:signIn')


def terms_and_conditions(request):
    """Display and handle acceptance of terms and conditions."""
    if request.method == 'POST':
        TermsAndConditions.objects.get_or_create(user=request.user, accepted=True)
        return redirect('userauth:completeProfile')
    return render(request, "userauth/termsAndconditions.html")


def complete_profile(request):
    """Complete user profile by updating connected accounts and redirecting to profile."""
    if request.method == 'POST':
        connected_accounts = ConnectedAccounts.objects.get(user=request.user)
        connected_accounts.connected = True
        connected_accounts.save()
        return redirect('profile_management:profile', username=request.user.username)
    
    context = {
        "connected_instagram_account": Instagram.objects.filter(user=request.user),
        "connected_facebook_account": Facebook.objects.filter(user=request.user),
    }
    return render(request, "userauth/completeProfile2.html", context)


def report_csp_violation(request):
    """Handle and log CSP violations for security analysis."""
    if request.method == 'POST':
        report_data = json.loads(request.body)
        # Here you would log the report_data for analysis
        return HttpResponse(status=204)
    return HttpResponseBadRequest("Invalid request method")

