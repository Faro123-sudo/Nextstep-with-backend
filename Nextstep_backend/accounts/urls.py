from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    RegisterView, 
    LoginView, 
    ProfileView, 
    UpdateProfileView, 
    ChangePasswordView, 
    LogoutView, 
    CookieTokenObtainPairView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    # Token endpoints - choose TokenObtainPairView or CookieTokenObtainPairView
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # if you prefer cookies, use:
    # path("token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # user endpoints
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", UpdateProfileView.as_view(), name="profile_update"),
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
