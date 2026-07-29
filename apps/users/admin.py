from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ["phone_number", "full_name", "role", "is_active", "created_at"]
    list_filter   = ["role", "is_active"]
    search_fields = ["phone_number", "full_name"]
    ordering      = ["-created_at"]

    fieldsets = (
        (None,        {"fields": ("phone_number", "password")}),
        ("Personal",  {"fields": ("full_name",)}),
        ("Role",      {"fields": ("role",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("phone_number", "full_name", "password1", "password2", "role"),
        }),
    )