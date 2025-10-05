from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer, 
    RegisterSerializer, 
    ChangePasswordSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)

User = get_user_model()

# Registration
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

# Profile (get current user)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


# Logout / blacklist refresh (requires token_blacklist app)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Expect the refresh token in the body: {"refresh": "<token>"}
        If you are storing refresh in a cookie you can read it from request.COOKIES
        """
        refresh_token = request.data.get("refresh", None)
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


# Optional: token view that also sets httpOnly refresh cookie (if you prefer cookies)
#
# To enable cookie behavior set in settings.py:
# SIMPLE_JWT = {"SET_REFRESH_COOKIE": True, "REFRESH_COOKIE_NAME": "refresh_token", "REFRESH_COOKIE_PATH": "/api/auth/"}  # example
#
# Then use CookieTokenObtainPairView below in URLs instead of default TokenObtainPairView.
#
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Obtains token pair and optionally sets the refresh token in a httpOnly cookie.
    Controlled by SIMPLE_JWT['SET_REFRESH_COOKIE'] boolean in settings.py.
    """
    serializer_class = TokenObtainPairSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        # Not used here; override post below to set cookie.
        return super().finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if getattr(settings, "SIMPLE_JWT", {}).get("SET_REFRESH_COOKIE", False):
            refresh = response.data.get("refresh")
            cookie_name = getattr(settings, "SIMPLE_JWT", {}).get("REFRESH_COOKIE_NAME", "refresh_token")
            cookie_path = getattr(settings, "SIMPLE_JWT", {}).get("REFRESH_COOKIE_PATH", "/")
            secure = getattr(settings, "SIMPLE_JWT", {}).get("REFRESH_COOKIE_SECURE", False)
            samesite = getattr(settings, "SIMPLE_JWT", {}).get("REFRESH_COOKIE_SAMESITE", "Lax")

            # Set httpOnly cookie
            response.set_cookie(cookie_name, refresh, httponly=True, secure=secure, samesite=samesite, path=cookie_path)
            # Optionally remove the refresh token from response body so only cookie holds it:
            if getattr(settings, "SIMPLE_JWT", {}).get("HIDE_REFRESH_IN_RESPONSE", False):
                response.data.pop("refresh", None)
        return response


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import UserSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)
