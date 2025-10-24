from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate using either email (case-insensitive) or username.

        Accepts either the positional/keyword `username` or an `email` kwarg
        (some callers pass email as a kwarg). Performs case-insensitive
        lookup on the email field to avoid simple casing mismatches.
        """
        UserModel = get_user_model()

        lookup_value = username or kwargs.get('email') or kwargs.get('username')
        if not lookup_value:
            return None

        try:
            # Try case-insensitive email first
            user = UserModel.objects.get(email__iexact=lookup_value)
        except UserModel.DoesNotExist:
            # Fall back to username exact match
            try:
                user = UserModel.objects.get(username=lookup_value)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password):
            return user
        return None

class JWTCookieAuthentication(JWTAuthentication):
    """
    An authentication class that extends JWTAuthentication to read the JWT
    from an httpOnly cookie.
    """
    def authenticate(self, request):
        # First, try the standard Authorization header flow
        try:
            header_result = super().authenticate(request)
            if header_result is not None:
                logger.debug("Authenticated via Authorization header")
                return header_result
        except Exception as e:
            # log and continue to cookie-based fallback
            logger.debug("Header-based JWT auth failed: %s", e)

        # Fallback: try access token in cookie
        cookie_name = getattr(settings, 'SIMPLE_JWT', {}).get('ACCESS_TOKEN_COOKIE_NAME', 'access_token')
        raw_token = request.COOKIES.get(cookie_name)
        if not raw_token:
            logger.debug("No access token cookie present (cookie name: %s)", cookie_name)
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            logger.debug("Authenticated via cookie token")
            return self.get_user(validated_token), validated_token
        except Exception as e:
            logger.warning("Cookie-based JWT validation failed: %s", e)
            return None