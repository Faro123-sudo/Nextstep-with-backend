from django.urls import path
from .views import (
    RegisterView,
    ProfileView,
    UpdateProfileView,
    ChangePasswordView,
    LoginAPIView,
    RefreshAPIView,
    LogoutAPIView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # 🔐 Auth & Tokens
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/", RefreshAPIView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),

    # 👤 User management
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", UpdateProfileView.as_view(), name="profile_update"),
    path("password/change/", ChangePasswordView.as_view(), name="password_change"),

    # 🔄 Password reset
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
