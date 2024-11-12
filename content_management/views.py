"""
Post Management Views for the post management app.
Includes functions for creating, updating, and deleting user posts,
handling various content types (text, image, video),
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib import messages
from django.utils import timezone
import logging

from userauth.models import UserProfile, Post
from django.contrib.auth.decorators import login_required

# Initialize logger
logger = logging.getLogger(__name__)

@login_required
def create(request):
    """
    Handles post creation for the logged-in user, including text, image, and video posts.
    Returns post statistics and recent posts to the template for display.
    """
    user = request.user

    # Fetch the user's profile and log errors if UserProfile does not exist
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        logger.error(f"UserProfile for user {user.username} does not exist.")
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('some_fallback_view')  # Redirect to a fallback view in case of error

    # Fetch post counts and recent posts for the user
    try:
        total_posts = Post.objects.filter(user=user).count()
        image_posts = Post.objects.filter(user=user, content_type="image").count()
        video_posts = Post.objects.filter(user=user, content_type="video").count()
        text_posts = Post.objects.filter(user=user, content_type="text").count()
        recent_posts = Post.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Handle case when there are no posts
        latest_post = Post.objects.filter(user=user).latest('created_at')
    except ObjectDoesNotExist:
        latest_post = None
        logger.info(f"No posts found for user {user.username}.")

    # Handle form submissions based on post type
    if request.method == 'POST':
        try:
            if 'twitte_submit' in request.POST:
                twitte = request.POST.get('twitte')
                if twitte:
                    Post.objects.create(user=user, content_type='text', content=twitte)
                    messages.success(request, "Text post created successfully.")
                    logger.info(f"Text post created by user {user.username}. Content: {twitte}")
                else:
                    messages.warning(request, "Text content cannot be empty.")

            elif 'image_submit' in request.POST:
                image = request.FILES.get('image')
                caption = request.POST.get('caption', '')
                if image:
                    Post.objects.create(user=user, content_type="image", media_file=image, content=caption)
                    messages.success(request, "Image post created successfully.")
                    logger.info(f"Image post created by user {user.username}. Image: {image.name}")
                else:
                    messages.warning(request, "Image upload failed. No image provided.")

            elif 'video_submit' in request.POST:
                video = request.FILES.get('video')
                caption = request.POST.get('caption', '')
                if video:
                    Post.objects.create(user=user, content_type="video", media_file=video, content=caption)
                    messages.success(request, "Video post created successfully.")
                    logger.info(f"Video post created by user {user.username}. Video: {video.name}")
                else:
                    messages.warning(request, "Video upload failed. No video provided.")

        except Exception as e:
            logger.error(f"Error while creating post for user {user.username}: {e}")
            messages.error(request, "There was an error while submitting your post. Please try again.")

    # Pass context data to the template
    context = {
        "user_profile": user_profile,
        "total_posts": total_posts,
        "text_posts": text_posts,
        "image_posts": image_posts,
        "video_posts": video_posts,
        "recent_posts": recent_posts,
        "latest_post": latest_post,
    }

    return render(request, "userauth/create.html", context)

@login_required
def update(request, pk):
    """
    Handles updating a post (text, image, or video) based on the content type. 
    Provides user feedback and handles potential errors during the update process.
    """
    post = get_object_or_404(Post, pk=pk)

    # Ensure the user is the owner of the post
    if post.user != request.user:
        logger.warning(f"Unauthorized update attempt by user {request.user.username} for post ID {post.pk}.")
        raise PermissionDenied("You are not authorized to update this post.")

    # Handle form submissions for updating post content
    if request.method == 'POST':
        try:
            if 'twitte_submit' in request.POST:
                twitte = request.POST.get('twitte')
                if twitte:
                    post.content = twitte
                    post.save()
                    messages.success(request, "Your text post was updated successfully.")
                    logger.info(f"Text post (ID: {post.pk}) updated by user {request.user.username}.")
                else:
                    messages.warning(request, "Text content cannot be empty.")

            elif 'image_submit' in request.POST:
                caption = request.POST.get('caption')
                if caption:
                    post.content = caption
                    post.save()
                    messages.success(request, "Your image post was updated successfully.")
                    logger.info(f"Image post (ID: {post.pk}) updated by user {request.user.username}.")
                else:
                    messages.warning(request, "Image caption cannot be empty.")

            elif 'video_submit' in request.POST:
                caption = request.POST.get('caption')
                if caption:
                    post.content = caption
                    post.save()
                    messages.success(request, "Your video post was updated successfully.")
                    logger.info(f"Video post (ID: {post.pk}) updated by user {request.user.username}.")
                else:
                    messages.warning(request, "Video caption cannot be empty.")

        except Exception as e:
            logger.error(f"Error updating post (ID: {post.pk}) for user {request.user.username}: {e}")
            messages.error(request, "There was an error updating your post. Please try again.")
        
        return redirect('profile_management:profile', username=request.user.username)

    # Pass the post object to the template for rendering the update form
    context = {
        "post": post,
    }

    return render(request, "userauth/update.html", context)

@login_required
def delete(request, pk):
    """
    Handles deletion of a post by the user. Provides proper error handling and user feedback.
    """
    post = get_object_or_404(Post, pk=pk)

    # Ensure that the user attempting to delete the post is the owner
    if post.user != request.user:
        logger.warning(f"Unauthorized deletion attempt by user {request.user.username} for post ID {post.pk}.")
        raise PermissionDenied("You are not authorized to delete this post.")

    try:
        # Delete the post and log the action
        post.delete()
        messages.success(request, "Post deleted successfully.")
        logger.info(f"Post ID {post.pk} deleted by user {request.user.username}.")
    except Exception as e:
        # Log any errors and inform the user
        logger.error(f"Error deleting post (ID: {post.pk}) for user {request.user.username}: {e}")
        messages.error(request, "An error occurred while trying to delete the post. Please try again later.")

    # Redirect back to the user's profile
    return redirect('profile_management:profile', username=request.user.username)
