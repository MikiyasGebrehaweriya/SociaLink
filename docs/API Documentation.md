# API Documentation

## API Overview
The application interacts through both server-side rendering (via Django templates) and backend logic (via Django views). The backend is responsible for handling HTTP requests, processing data, and interacting with databases through Django's ORM. Below is a detailed explanation of how various files like views.py, models.py, urls.py, and others work together in the authentication, management and other functionalities.

## views.py
This file contains the logic for handling user actions and processing requests. Below is a breakdown of each function and how they work:

### User Authentication

#### ``signIn(request)``

This view handles the user login functionality by verifying the provided username and password. If the credentials are valid, it logs the user in and then redirects them based on their terms and conditions acceptance and connected social media accounts. Here's how it works step by step:

* Input:
    * The POST request contains the following fields:
        * ``username``: The user's username (converted to lowercase).
        * ``password``: The user's password.
* Processing:
    1. Fetch the user:
        * The ``User.objects.get()`` method fetches the user from the database based on the provided username.
        * If the user does not exist, it raises a ``User.DoesNotExist`` exception, and an error message is displayed.
    2. Authenticate the user:
        * Django's ``authenticate()`` function is used to verify the username and password combination.
        * If the authentication is successful, the ``login()`` function is called, which logs the user into the session.
    3. Post-login flow:
        * After successful login, the system checks whether the user has accepted the terms and conditions via the ``TermsAndConditions`` model.
            * If they haven't, the user is redirected to the terms and conditions page.
        * The system also checks whether the user has connected any social media accounts via the ``ConnectedAccounts`` model.
            * If they have connected accounts, the user is redirected to their profile page.
            * If they haven't connected any accounts, they are redirected to the "complete profile" page to finish their profile setup.
    4. Error Handling:
        * If the credentials are invalid, an error message is displayed, informing the user that the username or password is incorrect.

* Outcome:
    * Success: The user is logged in and redirected to either:
        * Their profile page if they have connected accounts.
        * The profile completion page if accounts are not connected.
        * The terms and conditions page if they haven't accepted the terms.
    * Failure: Error messages are displayed in the template for:
        * Invalid credentials.
        * Non-existent user.

```py
def signIn(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            # Fetch the user by username
            user = User.objects.get(username=username)
            
            # Authenticate the user
            authenticated_user = authenticate(request, username=username, password=password)
            
            if authenticated_user is not None:
                # Log the user in
                login(request, authenticated_user)
                
                # Check if user accepted the terms and conditions
                if TermsAndConditions.objects.filter(user=request.user).exists():
                    # Check if connected accounts exist
                    if ConnectedAccounts.objects.filter(user=request.user, connected=True).exists():
                        return redirect('profile', username=request.user.username)
                    else:
                        return redirect('completeProfile')
                else:
                    return redirect('termsAndconditions')
            else:
                # Invalid credentials error
                messages.error(request, "Invalid username or password")
        
        except User.DoesNotExist:
            # User does not exist error
            messages.error(request, "User does not exist")
    
    context = {}
    return render(request, "userauth/signIn2.html", context)
```

* Django Components Involved:
    1. ``authenticate(request, username, password)``:
        * Verifies that the provided username and password match a user in the database.profile is complete.
    2. ``login(request, user)``:
        * Logs the user in by creating a session tied to that user.
    3. ``redirect()``:
        * Handles the redirection logic based on whether the user has accepted the terms and conditions or has connected accounts.
    4.  ``messages.error()``:
        * Used to pass error messages to the template, informing the user of login issues like incorrect credentials or non-existent users.

* Models Involved:
    * ``User``: The default Django user model used to store and authenticate credentials.
    * ``TermsAndConditions``: Custom model to track if a user has accepted the platform's terms.
    * ``ConnectedAccounts``: Custom model to track whether a user has connected any social media accounts like Instagram or Facebook.

#### ``signUp(request)``
This view handles user registration by processing the user's input, creating a new user account, generating a personalized QR code, and assigning a unique code to the user. If successful, the user is logged in and redirected to accept the terms and conditions. Here is how the process works step-by-step:

* Input:
    * The POST request contains:
        * ``username``: The username provided by the user (converted to lowercase).
        * Other fields required by ``MyUserCreationForm`` (e.g., email, password, etc.).

* Processing:
    1. Handle the registration form:
        * An instance of ``MyUserCreationForm`` is created to handle form input.
        * If the form data is valid, the user object is created using ``form.save(commit=False)`` and saved to the database with the username in lowercase.
    2. Log the user in:
        * Once the user is successfully created, the ``login()`` function is called to automatically log them in.
    3. Generate a QR Code:
        * After registration, a QR code is generated for the user. This QR code encodes the URL of the user's profile page (e.g., ``/profile/{username}/``).
        * The QR code is created using the ``qrcode`` library with specific settings (version, error correction, box size, border).
        * The generated QR code image is customized with fill and background colors, and saved as an image file under the ``qrcodes`` directory inside the media root.
    4. Generate a unique user code:
        * A unique number is generated using the ``generate_unique_number()`` function, which can serve as a user identifier or verification code.
    5. Create a UserProfile:
        * A ``UserProfile`` object is created for the newly registered user.
        * The QR code image path and unique user code are saved in the user's profile.
    6. Redirect to terms and conditions:
        * After the user has been created and logged in, they are redirected to the terms and conditions page.
    7. Form validation:
        * If the form is not valid, the errors are caught and displayed to the user using Django's ``messages.error()`` system.

* Outcome:
    * Success: The user is created, logged in, and a QR code is generated. The user is then redirected to the terms and conditions page.
    * Failure: If form validation fails, error messages are displayed to guide the user in correcting the input.

```py
def signUp(request):
    user_form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # Save user with lowercase username
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            # Log the user in
            login(request, user)
            
            # Generate QR code content (e.g., user profile URL)
            qr_content = request.build_absolute_uri(f'/profile/{user.username}/')
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#135D66", back_color="#FFF5E0")
            
            # Save QR code image to the "qrcodes" folder
            media_root = settings.MEDIA_ROOT
            qrcodes_folder = os.path.join(media_root, 'qrcodes')
            if not os.path.exists(qrcodes_folder):
                os.makedirs(qrcodes_folder)
            qr_img_path = os.path.join(qrcodes_folder, f'{user.username}_qr.png')
            qr_img.save(qr_img_path)
            
            # Generate a unique user code
            unique_number = generate_unique_number()
            print(unique_number)
            
            # Create a UserProfile and save QR code and user code
            user_profile = UserProfile.objects.create(user=user)
            user_profile.qr_code = qr_img_path
            user_profile.user_code = unique_number
            user_profile.save()
            
            return redirect('termsAndconditions')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
       
    context = {
        'user_form': user_form,
    }
    return render(request, "userauth/signUp2.html", context)
```

* Django Components Involved:
    1. ``MyUserCreationForm``: Custom form for user registration, used to capture and validate user details.
    2. ``login(request, user)``: Logs the newly registered user in by creating a session for them.
    3. ``qrcode``: Python library used to generate a QR code with the user's profile URL as its content.
    4. ``os.path`` & ``os.makedirs()``: Used to check and create the necessary folder structure for storing QR code images.
    5. ``messages.error()``: Used to display form validation errors in the template for user feedback.

* Models Involved:
    * ``User``: The standard Django user model that stores basic user information like username and password.
    * ``UserProfile``: Custom model that stores additional information about the user, including the QR code path and a unique user code.
    * ``generate_unique_number()``: Custom function responsible for generating a unique identifier for the user.

#### ``signOut(request)``
This view handles user logout, ensuring that the user's session is terminated and they are redirected to the sign-in page. It performs a simple but essential process to securely log the user out of the application.

* Input:
    * The request does not require any specific input, as the logout action is initiated when a user triggers the sign-out process (typically by clicking a "Logout" button or link).

* Processing:
    1. User Logout:
        * The ``logout()`` function from Django's authentication framework is called. This function:
            * Clears the session data for the current user.
            * Terminates the user's active session in the application.
    2. Redirect to Sign-In Page:
        * Once the user is logged out, they are redirected to the ``signIn`` view where they can log in again if desired.

* Outcome:
    * Success: The user is logged out and redirected to the sign-in page.
    * Failure: No specific failure scenario as the ``logout()`` function is a simple action with minimal chances of error.

```py
def signOut(request):
    logout(request)
    return redirect('signIn')
```

* Django Components Involved:
    1. ``logout()``: This function from Django's authentication system logs the user out by clearing their session.
    2. ``redirect()``: After logging out, this function redirects the user to the 'signIn' page, ensuring they are no longer in an authenticated state.

### Profile Management

#### ``profile(request, username)``
This view is responsible for rendering a user's profile page, showing various social media data, posts, and connections, while also differentiating between the profile owner and visitors. Here's an overview of how the process works:

* Input:
    * The function receives a ``request`` object and the ``username`` of the user whose profile is being viewed.
    * The view checks if the profile belongs to the currently logged-in user (``is_own_profile``) or is being accessed by another user.

* Processing:
    1. Retrieve User Profile:
        * The ``get_object_or_404()`` function retrieves the ``User`` object associated with the ``username`` passed in the URL.
        * The ``UserProfile`` object for the logged-in user (``request.user``) is fetched to display their own profile information.
    2. Check Ownership of Profile:
        * The view checks if the logged-in user (``request.user``) is viewing their own profile by comparing their username with the profile being viewed (``is_own_profile``).
    3. Fetch Profile Data:
        * The profile's associated posts, connected social media accounts (Instagram, Facebook), and recently connected users are retrieved.
        * Connected accounts like Instagram, Facebook, YouTube, LinkedIn, Google, X (formerly Twitter), and TikTok are checked, and the total number of connected platforms is calculated.
    4. Instagram API Call:
        * The view makes an API call to Instagram's Graph API using the user's Instagram access token to fetch recent media (e.g., posts, captions, media URLs).
        * The fetched data is saved to the Instagram model for future access.
    5. Facebook API Call:
        * Similarly, the Facebook Graph API is used to fetch data about the user's Facebook profile (e.g., name, email, posts, photos).
        * The response is saved to the Facebook model, or an error message is printed if the call fails.
    6. Other Data:
        * The 5 most recent posts of the connected users are fetched, along with other users' profiles for display in the user interface.
        * The user's profile form is also rendered for potential updates.

* Outcome:
    * Success: The profile page is rendered with all the user’s profile details, including connected accounts and recent posts.
    * Failure: If there is an error in fetching social media data, appropriate error messages are printed.

```py
def profile(request, username):
    profile = get_object_or_404(User, username=username)
    logged_user_profile = UserProfile.objects.get(user=request.user)
    is_own_profile = request.user.is_authenticated and str(request.user) == str(profile.username)
    
    user = User.objects.get(username=username)
    user_profile = UserProfile.objects.get(user=user)
    list_of_users_profile = UserProfile.objects.exclude(user=user).order_by('-created_at')[:5]
    profile_form = UserProfileForm(instance=request.user)
    
    instagram = Instagram.objects.get(user=user)
    facebook = Facebook.objects.get(user=user)
    
    posts = Post.objects.filter(user=user).order_by('-created_at')
    connected_users = Connection.objects.filter(user=user).values_list('connected_user', flat=True)
    recent_posts_form_connected_users = Post.objects.filter(user__in=connected_users).order_by('-created_at')[:4]
    
    connected_instagram_account = Instagram.objects.filter(user=user)
    connected_facebook_account = Facebook.objects.filter(user=user)
    
    user_connected_account = ConnectedAccounts.objects.get(user=user)
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
```

* Django Components Involved:
    1. ``get_object_or_404()``: Fetches the user's profile, or raises a 404 error if the user is not found.
    2. ``request.user.is_authenticated``: Checks if the logged-in user is authenticated.
    3. ``requests.get()``: Sends API requests to Instagram and Facebook to fetch user data.
    4. ``render()``: Renders the profile page with the gathered data and context.

* Models Involved:
    * User: Stores basic user information (username).
    * UserProfile: Handles extended profile data, like user codes and connected accounts.
    * Instagram/Facebook: Models to store data fetched from respective social media APIs.
    * Post: Fetches the user’s posts and those of their connected users.
    * ConnectedAccounts: Tracks the user's connected social media accounts.

#### ``instagramAuthorize(request)``
This view handles initiating the Instagram OAuth authorization process for users by generating a CSRF token and constructing the authorization URL. It redirects the user to Instagram's authorization page to give permission for the app to access their profile and media data.

* Input:
    * The view takes a ``request`` object.

* Processing:
    1. Generate CSRF Token:
        * A CSRF token is generated using ``get_token(request)`` to protect against cross-site request forgery (CSRF) attacks.
        * The CSRF token is stored in the user's session (``request.session['instagram_csrf_token']``) for later verification during the callback phase.
    2. Construct Instagram Authorization URL:
        * The view creates an Instagram authorization URL that includes:
            * ``client_id``: The application's Instagram client ID.
            * ``redirect_uri``: The URL to which Instagram will redirect after authorization (in this case, ``https://127.0.0.1:4000/instagram_callback/``).
            * ``scope``: The permissions requested (e.g., ``user_profile``, ``user_media``).
            * ``response_type``: Specifies that the app is expecting an authorization code.
            * ``state``: Includes the CSRF token for security and integrity verification during the OAuth process.
    3. Redirect User:
        * The user is redirected to the Instagram authorization page, where they will be asked to grant the app access to their profile and media data.

* Outcome:
    * Success: The user is redirected to the Instagram OAuth authorization page to give permission.
    * Failure: If any issue occurs with constructing the URL, the redirect will fail (although this is unlikely with correct setup).

```py
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
```

* Django Components Involved:
    1. ``get_token(request)``: Generates a CSRF token to protect against CSRF attacks.
    2. ``request.session[]``: Stores the CSRF token in the session for future verification during the callback phase.
    3. ``redirect()``: Redirects the user to Instagram's OAuth authorization page after constructing the URL.
    4. OAuth Process: This function prepares the app for the Instagram OAuth flow by redirecting users to the authorization URL. The app requests access to the user's profile and media data by specifying the required scopes (``user_profile``, ``user_media``).

#### ``instagramCallback(request)``
This view handles the callback after a user authorizes the app on Instagram. It exchanges the authorization code for an access token and stores user data in the database. Additionally, it validates the CSRF token and converts a short-lived access token into a long-lived one.

* Input:
    * The view takes a ``request`` object containing query parameters like the authorization ``code`` and ``state`` for CSRF verification.

* Processing:
    1. Extract Parameters:
        * Extracts the authorization ``code`` and ``state`` (CSRF token) from the query parameters in the request.
    2. CSRF Validation:
        * Retrieves the CSRF token saved in the session during the authorization phase.
        * Compares the ``state`` parameter (which contains the CSRF token) with the one stored in the session. If they don't match, an error message is displayed, and the user is redirected to the ``completeProfile`` page.
    3. Exchange Code for Access Token:
        * If CSRF validation succeeds, a POST request is sent to Instagram's OAuth API to exchange the authorization code for an access token. This step converts the code obtained during authorization into an actual token for accessing Instagram's resources.
    4. Process the Access Token Response:
        * If the response is successful, the access token and user ID are extracted from the response.
    5. Check for Existing Instagram Account:
        * The app checks if the Instagram account (``instagram_id``) already exists in the database. If not, it proceeds with generating a long-lived access token.
    6. Exchange Short-Lived Token for Long-Lived Token:
        * If the account is new, a GET request is made to exchange the short-lived token for a long-lived token, which is valid for a longer period (usually 60 days).
    7. Fetch Instagram Username:
        * The app makes another GET request to the Instagram API to fetch the username associated with the account using the access token.
    8. Save Data to Database:
        * A new Instagram account object is created in the ``Instagram`` model, storing the access token, username, and expiration details. It also updates the ``ConnectedAccounts`` model by incrementing the ``instagram`` attribute for the user.
    9. Handle Existing Account:
        * If the Instagram account already exists, an error message is displayed.
    10. Redirect User:
        * After the process, the user is redirected to the ``completeProfile`` page regardless of success or failure.

* Outcome:
    * Success: Instagram access token is successfully retrieved, saved in the database, and linked to the user's account.
    * Failure: If an error occurs (e.g., CSRF validation failure or Instagram authorization issues), appropriate error messages are displayed.

```py
def instagramCallback(request):
    # Extract the access code and state from the query parameters
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # Retrieve the CSRF token from session
    csrf_token = request.session.get('instagram_csrf_token')

    # Check if the state parameter matches the CSRF token
    if not constant_time_compare(csrf_token, state):
        # Handle CSRF validation failure
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
            # Exchange the short-lived access token for a long-lived one
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': INSTAGRAM_CLIENT_SECRET,
                'access_token': access_token,
            }
            ex_change_token = requests.get('https://graph.instagram.com/access_token', params=params)
            
            # Process the exchanged response and extract the long-lived access token and expiration date
            if ex_change_token.status_code == 200:
                ex_change_token = ex_change_token.json()
                long_lived_token = ex_change_token.get('access_token')
                long_lived_token_type = ex_change_token.get('token_type')
                long_lived_token_expires_in = ex_change_token.get("expires_in")
                expires_at = timezone.now() + timedelta(seconds=long_lived_token_expires_in)
                
                # Fetch the Instagram username
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
                
                # Save Instagram account details
                Instagram.objects.create(
                    user=request.user,
                    instagram_id=instagram_user_id,
                    instagram_name=instagram_name,
                    token=long_lived_token, 
                    token_type=long_lived_token_type,
                    expires=expires_at
                )
                
                # Update ConnectedAccounts
                connected_accounts, created = ConnectedAccounts.objects.get_or_create(user=request.user)
                connected_accounts.instagram += 1
                connected_accounts.save()
        else:
            messages.error(request, "Account Already Connected")  
            
    else:
        print("Not Authorized By Instagram")
        
    return redirect('completeProfile')
```

* Django Components Involved:
    1. ``get_token()``: Used to retrieve CSRF tokens for security purposes.
    2. ``requests.post()`` and ``requests.get()``: Python's ``requests`` library is used to make HTTP requests to Instagram's OAuth and API endpoints.
    3. Models: The app interacts with several models like ``Instagram``, ``ConnectedAccounts`` to save user data and account connections.
    4. ``messages.error()``: Used to display error messages to users.
    5. ``constant_time_compare()``: Compares CSRF tokens securely.