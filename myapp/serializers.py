# serializers.py
from rest_framework import serializers
from .models import AuthorProfile

class AuthorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = ['bio', 'profile_picture', 'website', 'metier', 'facebook', 'twitter', 'gmail', 'is_author']  # Include fields you want to be editable
        read_only_fields = ('user',)  # User should not be editable through the serializer