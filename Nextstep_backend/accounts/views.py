from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import UserToken
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    LoginSerializer,
)

User = get_user_model()

# ---------------- REGISTER ----------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# ---------------- PROFILE ----------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data})


class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# ---------------- CHANGE PASSWORD ----------------
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


# ---------------- LOGIN ----------------
@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Log incoming payload for debugging
        logger.debug("Login request data: %s", request.data)
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            logger.warning("Login validation failed: %s", serializer.errors)
            serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Save tokens in DB
        UserToken.objects.update_or_create(
            user=user,
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )

        # Send refresh token in HttpOnly cookie
        response = Response(
            {
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "access": access_token,
            },
            status=status.HTTP_200_OK,
        )

        # In development include the refresh token in the JSON body to support the SPA
        if settings.DEBUG:
            response.data["refresh"] = refresh_token

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,  # Secure=True in production
            samesite="Lax",
        )

        return response


# ---------------- REFRESH ----------------
@method_decorator(csrf_exempt, name='dispatch')
class RefreshAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Try cookie-based refresh first
        refresh_token = request.COOKIES.get("refresh_token")
        logger.debug("Refresh called; cookies: %s", request.COOKIES.keys())

        # Fallback: accept JSON refresh token in request body (useful for SPA local dev)
        if not refresh_token:
            body_refresh = request.data.get('refresh') if hasattr(request, 'data') else None
            if body_refresh:
                refresh_token = body_refresh

        if not refresh_token:
            return Response({"error": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            user_id = token.payload.get("user_id")

            # Update access token in DB
            UserToken.objects.filter(user_id=user_id).update(access_token=access_token)

            return Response({"access": access_token}, status=status.HTTP_200_OK)

        except TokenError:
            logger.warning("Refresh failed - invalid or expired token")
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# ---------------- LOGOUT ----------------
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Remove from DB
            UserToken.objects.filter(user=request.user).delete()

            # Clear cookies
            response = Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("refresh_token")

            return response

        except Exception:
            return Response({"error": "Logout failed."}, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------------------------------------------------
# 🔐 PASSWORD RESET
# ---------------------------------------------------------------------

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')

        response_detail = "If an account with that email exists, a password reset link has been sent."

        if user:
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password-confirm?uid={uidb64}&token={token}"

            email_context = {'user': user, 'reset_link': reset_link}
            html_content = render_to_string('password_reset_email.html', email_context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject="Reset Your Password",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        return Response({"detail": response_detail}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

