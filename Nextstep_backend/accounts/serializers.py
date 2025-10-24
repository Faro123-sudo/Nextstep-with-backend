from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    education_level = serializers.CharField(source='profile.education_level', read_only=True)
    bio = serializers.CharField(source='profile.bio', read_only=True)
    interests = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='profile.interests')
    class Meta:
        model = User
        # include all fields from the model
        fields = ("id", "username", "email", "first_name", "last_name", "role", "bio", "education_level", "interests")
        read_only_fields = ("id",)


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
            # Allow username to be provided by the client. If omitted, we'll default to email.
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
        # Use provided username if present, otherwise default username to the email
        username = validated_data.get('username') or validated_data.get('email')
        validated_data['username'] = username
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

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        email = data.get('email')
        # Look up the user
        user = User.objects.filter(email__iexact=email).first()
        data['user'] = user
        return data
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True, required=True)
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, data):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.user = None

        if self.user is None or not default_token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError("Invalid password reset link.")

        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Passwords must match."})

        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        return self.user

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        # Some authentication backends expect the request to be passed in
        request = self.context.get('request')
        user = authenticate(request=request, username=email, password=password)

        if not user:
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials"]})

        if not user.is_active:
            raise serializers.ValidationError({"non_field_errors": ["This account is inactive"]})

        data["user"] = user
        return data