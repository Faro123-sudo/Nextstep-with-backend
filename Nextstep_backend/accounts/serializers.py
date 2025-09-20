from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # include all fields from the model
        fields = ("id", "username", "email", "first_name", "last_name", "role", "bio")
        read_only_fields = ("id",)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User  # Ensure you are importing your custom User model

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True, 
        label="Confirm password",
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        # Add "role" to the fields tuple
        fields = ("username", "email", "password", "password2", "first_name", "last_name", "role")
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "role": {"required": True},
        }

    def validate(self, data):
        """Check that both passwords match."""
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
