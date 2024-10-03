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

