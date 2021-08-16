from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import CustomUser


class MyRegisterSerializer(serializers.Serializer):
    class Meta:
        module = CustomUser

    email = serializers.EmailField()
    password = serializers.CharField(validators=[validate_password])

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        return MyLogInSerializer(instance).data


class MyLogInSerializer(serializers.Serializer):
    class Meta:
        module = CustomUser

    email = serializers.EmailField()
    password = serializers.CharField()

    def save(self, **kwargs):
        return self.validated_data

    def validate(self, data):
        """
        Gotta make sure the person can be logged in
        """
        user = authenticate(username=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Incorrect credentials.")
        return user

    def to_representation(self, instance):
        representation = {}

        # Gotta check if there's a token and create it if not
        # Then we send the token but in the user one cuz it's easier?
        token, _ = Token.objects.get_or_create(user=instance)
        representation['access_token'] = str(token)
        return representation
