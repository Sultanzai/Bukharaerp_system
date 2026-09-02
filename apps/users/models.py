from django.db import models


class UserProfile(models.Model):
    """
    Additional information for the Django built-in User.
    """

    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username