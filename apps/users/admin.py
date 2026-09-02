from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
    )

    list_filter = (
        "created_at",
    )