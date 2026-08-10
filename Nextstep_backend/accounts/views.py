from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.throttling import ScopedRateThrottle

from .serializers import (
    UserSerializer, 
    RegisterSerializer, 
    ChangePasswordSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)

User = get_user_model()


# SimpleJWT views with scoped throttling
class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


class ThrottledTokenVerifyView(TokenVerifyView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


# ---------------------------------------------------------------------------
# Overview / Flow (accounts app)
# ---------------------------------------------------------------------------
#
# - Registration: `RegisterView` accepts user details and creates a new user
#   using `RegisterSerializer`. Password validation is enforced at serializer
#   level. After registration the client can call `login/` to obtain JWT tokens.
#
# - Authentication: JWT tokens are issued by SimpleJWT views. We subclass
#   those views (ThrottledToken*) to attach scoped throttling (scope 'auth')
#   to protect login/token endpoints from abuse.
#
# - Profile: `ProfileView` returns the current authenticated user's serialized
#   profile. `UpdateProfileView` allows partial updates to the user's profile.
#
# - Password Flow:
#   * `PasswordResetRequestView` accepts an email and (if present) sends a
#     password-reset link to the user's email. For security it always returns
#     the same success message to avoid user enumeration.
#   * `PasswordResetConfirmView` validates the uid/token combo and sets the
#     new password.
#   * `ChangePasswordView` requires the user's old password and enforces
#     password validators for the new password.
#
# - Logout: `LogoutView` blacklists refresh tokens (requires the
#   `rest_framework_simplejwt.token_blacklist` app and migrations).
#
# Notes:
# - Throttling is applied to sensitive endpoints to limit brute-force and
#   automated abuse. Email sending uses `DEFAULT_FROM_EMAIL` and in DEBUG
#   mode falls back to console backend to avoid accidental sends.
# ---------------------------------------------------------------------------

# Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

# Profile (get current user)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data})

# Update profile (partial)
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# Change password
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)


# Password Reset
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# views.py

# ... (imports remain the same) ...

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the user. It could be None if the email didn't exist, 
        # but the serializer passed validation for security reasons.
        user = serializer.validated_data.get('user') 

        # SECURITY: Always return a success message immediately 
        # to prevent user enumeration.
        response_detail = "If an account with that email exists, a password reset link has been sent."
        
        # Only proceed with email sending if a user was actually found.
        if user:
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            # Construct the full reset URL
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password-confirm?uid={uidb64}&token={token}"

            # Render email from template
            email_context = {
                'user': user,
                'reset_link': reset_link,
            }
            html_content = render_to_string('password_reset_email.html', email_context)
            text_content = strip_tags(html_content) 

            # Create and send the email
            email = EmailMultiAlternatives(
                subject="Reset Your Password for NextStep Navigator",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        # IMPORTANT: Return a success response regardless of whether 
        # an email was sent or not.
        return Response({"detail": response_detail}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


# Logout / blacklist refresh (requires token_blacklist app)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
