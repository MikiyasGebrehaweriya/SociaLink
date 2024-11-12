# Procedural Instructions

## User Authentication

### Sign Up
* Users are required to provide a username, email address and a password to sign up.
* Password Requirements: At least 8 characters, containing one uppercase letter, one lowercase letter, one number, and one special character.
* Upon submission, the system validates the provided data (ensuring the email format is correct, the password meets security standards, and no existing account uses the same email and username).
* A verification link is sent to the provided email to confirm the account.
* Once validated, a new `User` and associated `UserProfile` are created in the database using Django's `User` and `UserProfile` models.

### Sign In
* Users must provide the email and password they registered with.
* The system uses Django's built-in authentication methods to verify the credentials. If valid, the user is logged in, and a session is created.
* Upon successful authentication, the user is redirected to their profile dashboard.
* If the credentials are incorrect, an error message is displayed, and the user is prompted to try again upto 3 times everytime.

### Sign Out
* When users sign out, Django invalidates their session and clears any authentication tokens.
* This ensures they cannot access restricted pages unless they log in again.

## Profile Management

### Complete Profile
* After account creation, users are prompted to complete their profile. They can upload a profile picture, add a bio, and connect social media accounts.
* Uploaded images are handled via Django’s ImageField and stored in the designated media directory. A default profile picture is used if none is uploaded.
* User-specific QR codes are also generated and stored for future sharing.

### Update Profile
* Users can update personal information, such as their full name, bio, profile picture, and social media connections, via their profile settings.
* The system handles file uploads using Django's form validation and saves updated profile data to the `UserProfile` model.

## Social Media Integration

### Connect Accounts
* Users can link their social media accounts (Facebook, Instagram, LinkedIn, etc.) by clicking on the respective social media icons in the profile settings.
* This action redirects the user to the corresponding OAuth authorization page, where they must approve access.
* Upon successful authorization, a token is stored in the database (models like `Facebook`, `Instagram`, etc.) for future API interactions.

### Sync Data
* After authentication, the system uses the OAuth tokens to fetch relevant data from the connected accounts.
* Data from social media platforms, such as user posts and metadata, is stored in `data` fields (as JSON) in their respective models (e.g., `Facebook`, `Instagram`).

## Content Management

### Create Post
* Users can create a new post via a form where they select the content type: text, image, or video.
* If an image or video is selected, the file is uploaded using Django's `FileField`, which ensures appropriate file storage and access.
* The post is stored in the `Post` model, which includes fields for the content type, media files, and any associated metadata (timestamps, content description).

### Update Post
* Users can edit existing posts. When editing a post, they can change the content type (switch from text to image, for example), upload a new media file, or update the description.
* The `updated_at` field in the `Post` model is automatically updated whenever a post is modified.

### Delete Post
* Users can delete posts by calling a specific URL with the post’s primary key (`pk`). Once confirmed, the system removes the post from the database and deletes associated media files from the server storage.

## Content Sharing Across Social Media Platforms
After a user creates, updates, or deletes a post (whether it’s a text, image, or video), the system provides the option to synchronize these changes across any linked social media accounts (such as Facebook, Instagram, LinkedIn, etc.). Here’s how the process works:

* The system retrieves the necessary authentication tokens from the respective social media models (e.g., `Facebook`, `Instagram`, `LinkedIn`), which were stored when the user linked their accounts.
* Using these tokens, the system interacts with the APIs of the respective platforms to carry out the desired action (create, update, or delete) on the user’s behalf.
* For each action, the system logs the status of the process (successful or failed) and handles any errors that occur, such as expired tokens, invalid post IDs, or platform-specific restrictions. In such cases, the user is notified.

## Synchronization
For each action (create, update, or delete), the system maintains synchronization with the external platforms:

* The `lastsync` field in the corresponding social media models (e.g., `Facebook`, `Instagram`, etc.) is updated to track the most recent interaction with the respective platform.
* The `ConnectedAccounts` model tracks the status of linked accounts, providing feedback to users about whether their content has been successfully posted, updated, or deleted across the connected platforms.