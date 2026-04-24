from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """커스텀 유저 어드민"""
    model = CustomUser
    list_display = ("username", "email", "nickname", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "nickname")

    # 기존 UserAdmin fieldsets에 추가 필드 삽입
    fieldsets = UserAdmin.fieldsets + (
        ("추가 정보", {
            "fields": ("nickname", "interest_stocks", "profile_image"),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("추가 정보", {
            "fields": ("nickname", "interest_stocks", "profile_image"),
        }),
    )
