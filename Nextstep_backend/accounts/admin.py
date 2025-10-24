from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Fields to display in the user list in admin
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "role")
    search_fields = ("username", "email", "first_name", "last_name", "role")
    ordering = ("username",)

    # Customizing the user detail form in admin
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "bio", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields used when creating a new user from the admin panel
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "bio", "is_staff", "is_active"),
        }),
    )

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    readonly_fields = ('access_token', 'refresh_token')