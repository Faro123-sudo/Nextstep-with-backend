from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class JWTCookieAuthentication(JWTAuthentication):
    """
    An authentication class that extends JWTAuthentication to read the JWT
    from an httpOnly cookie.
    """
    def authenticate(self, request):
        cookie_name = getattr(settings, 'SIMPLE_JWT', {}).get('ACCESS_TOKEN_COOKIE_NAME', 'access_token')
        raw_token = request.COOKIES.get(cookie_name)
        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token