from django.test import TestCase
from django.contrib.auth.models import User
from userauth.models import UserProfile, Post
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class ContentManagementTests(TestCase):

    def setUp(self):
        """Set up test users and their profiles."""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user)

    def test_create_text_post(self):
        """Test creating a text post."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('content_management:create'), {'twitte_submit': 'submit', 'twitte': 'This is a test tweet!'})
        self.assertContains(response, "Text post created successfully.")
        self.assertTrue(Post.objects.filter(user=self.user, content_type='text', content='This is a test tweet!').exists())

    def test_create_image_post(self):
        """Test creating an image post."""
        self.client.login(username='testuser', password='testpassword')
        image_file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('content_management:create'), {'image_submit': 'submit', 'image': image_file, 'caption': 'Test image caption'})
        self.assertContains(response, "Image post created successfully.")
        self.assertTrue(Post.objects.filter(user=self.user, content_type='image', content='Test image caption').exists())

    def test_create_video_post(self):
        """Test creating a video post."""
        self.client.login(username='testuser', password='testpassword')
        video_file = SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")
        response = self.client.post(reverse('content_management:create'), {'video_submit': 'submit', 'video': video_file, 'caption': 'Test video caption'})
        self.assertContains(response, "Video post created successfully.")
        self.assertTrue(Post.objects.filter(user=self.user, content_type='video', content='Test video caption').exists())

    def test_create_post_empty_content(self):
        """Test creating a post with empty content."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('content_management:create'), {'twitte_submit': 'submit', 'twitte': ''})  # Empty twitte
        self.assertContains(response, "Text content cannot be empty.")

    def test_update_text_post(self):
        """Test updating a text post."""
        post = Post.objects.create(user=self.user, content_type='text', content='Original content')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('content_management:update', args=[post.pk]), {'twitte_submit': 'submit', 'twitte': 'Updated content'})
        self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
        post.refresh_from_db()
        self.assertEqual(post.content, 'Updated content')

    def test_update_image_post(self):
        """Test updating an image post's caption."""
        post = Post.objects.create(user=self.user, content_type='image', content='Original caption')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('content_management:update', args=[post.pk]), {'image_submit': 'submit', 'caption': 'Updated caption'})
        self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
        post.refresh_from_db()
        self.assertEqual(post.content, 'Updated caption')

    def test_update_video_post(self):
        """Test updating a video post's caption."""
        post = Post.objects.create(user=self.user, content_type='video', content='Original caption')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('content_management:update', args=[post.pk]), {'video_submit': 'submit', 'caption': 'Updated caption'})
        self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
        post.refresh_from_db()
        self.assertEqual(post.content, 'Updated caption')

    def test_delete_post(self):
        """Test deleting a post."""
        post = Post.objects.create(user=self.user, content_type='text', content='Test content')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('content_management:delete', args=[post.pk]))
        self.assertRedirects(response, reverse('profile_management:profile', kwargs={'username': 'testuser'}))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())


    def test_delete_post_unauthorized(self):
        """Test deleting a post by a user who is not the owner."""
        post = Post.objects.create(user=User.objects.create_user(username='anotheruser'), content_type='text', content='Test content')
        self.client.login(username='testuser', password='testpassword')
        
        # Expect a PermissionDenied exception
        with self.assertRaises(PermissionDenied):
            self.client.post(reverse('content_management:delete', args=[post.pk]))

        # Or, if you want to check the response directly (might need to adjust status code)
        # response = self.client.post(reverse('content_management:delete', args=[post.pk]))
        # self.assertEqual(response.status_code, 403)  # Forbidden