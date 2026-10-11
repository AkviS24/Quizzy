"""Database models for authentication-related state."""

from django.conf import settings
from django.db import models


class RevokedAccessToken(models.Model):
    """Store identifiers of access tokens revoked during logout."""

    jti = models.CharField(
        max_length=255,
        unique=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        """Return a readable description of the revoked token."""
        return f'Revoked token {self.jti}'
