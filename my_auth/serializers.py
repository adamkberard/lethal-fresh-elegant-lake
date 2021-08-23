from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import CustomUser


class MyRegisterSerializer(serializers.Serializer):
    """Serializer for registering users."""
    email = serializers.EmailField()
    password = serializers.CharField(validators=[validate_password])

    class Meta:
        module = CustomUser

    def validate_email(self, data):
        if CustomUser.objects.filter(email=data).exists():
            raise serializers.ValidationError("Email already in use.")
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        return MyLogInSerializer(instance).data


class MyLogInSerializer(serializers.Serializer):
    """Serializer for logging in users."""
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        module = CustomUser

    def save(self, **kwargs):
        return self.validated_data

    def validate(self, data):
        """
        Gotta make sure the person can be logged in with the given credentials
        """
        user = authenticate(username=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Incorrect credentials.")
        return user

    def to_representation(self, instance):
        rep = {}
        # This either creates a token for the user, or grabs an existing one
        token, _ = Token.objects.get_or_create(user=instance)
        rep['access_token'] = str(token)
        return rep
