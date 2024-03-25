from django.contrib import admin
from .models import UserProfile, TermsAndConditions, ConnectedAccounts, Facebook, Instagram, Youtube, Linkedin, Google, X, Tiktok


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'fullName', 'bio', 'profilePicture', 'qr_code']
    search_fields = ['user', 'fullName', 'bio', 'profilePicture', 'qr_code']
    list_filter = ['user', 'fullName', 'bio', 'profilePicture', 'qr_code']
    list_per_page = 25

class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['user', 'accepted', 'date_accepted']
    search_fields = ['user', 'accepted', 'date_accepted']
    list_filter = ['user', 'accepted', 'date_accepted']
    list_per_page = 25
    
class ConnectedAccountsAdmin(admin.ModelAdmin):
    list_display = ['user', 'connected', 'facebook', 'instagram', 'youtube', 'linkedin', 'google', 'x', 'tiktok']
    search_fields = ['user', 'connected', 'facebook', 'instagram', 'youtube', 'linkedin', 'google', 'x', 'tiktok']
    list_filter = ['user', 'connected', 'facebook', 'instagram', 'youtube', 'linkedin', 'google', 'x', 'tiktok']
    list_per_page = 25
    
class FacebookAdmin(admin.ModelAdmin):
    list_display = ['user', "facebook_id", "facebook_name", 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', "facebook_id", "facebook_name", 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', "facebook_id", "facebook_name", 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25
    
class InstagramAdmin(admin.ModelAdmin):
    list_display = ['user', 'instagram_id', "instagram_name", 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', 'instagram_id', "instagram_name", 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', 'instagram_id', "instagram_name", 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25

class YoutubeAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25
    
class LinkedinAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25
    
class GoogleAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25
    
class XAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25
    
class TiktokAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'token_type', 'expires', 'lastsync']
    search_fields = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_filter = ['user', 'token', 'token_type', 'expires', 'lastsync']
    list_per_page = 25
    
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
admin.site.register(ConnectedAccounts, ConnectedAccountsAdmin)
admin.site.register(Facebook, FacebookAdmin)
admin.site.register(Instagram, InstagramAdmin)
admin.site.register(Youtube, YoutubeAdmin)
admin.site.register(Linkedin, LinkedinAdmin)
admin.site.register(Google, GoogleAdmin)
admin.site.register(X, XAdmin)
admin.site.register(Tiktok, TiktokAdmin)