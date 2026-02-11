import uuid
from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # -------------------------------------------------
    # WHO performed the action
    # -------------------------------------------------
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # Snapshot identity (store EMAIL / USERNAME)
    username = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    # -------------------------------------------------
    # WHAT happened (technical + human readable)
    # -------------------------------------------------
    action = models.CharField(
        max_length=100
    )  # e.g. model.update, auth.login

    description = models.TextField(
        blank=True,
        default=""
    )  # e.g. "Updated student biodata of Mugizi Adrian"

    # -------------------------------------------------
    # REQUEST info
    # -------------------------------------------------
    path = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    method = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )

    status_code = models.IntegerField(
        null=True,
        blank=True
    )

    # -------------------------------------------------
    # DEVICE info
    # -------------------------------------------------
    device_id = models.CharField(
        max_length=64,
        blank=True,
        default=""
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True,
        default=""
    )

    session_key = models.CharField(
        max_length=40,
        blank=True,
        default=""
    )

    # -------------------------------------------------
    # OBJECT being affected
    # -------------------------------------------------
    app_label = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    model = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    object_id = models.CharField(
        max_length=64,
        blank=True,
        default=""
    )

    object_repr = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    # -------------------------------------------------
    # EXTRA metadata
    # -------------------------------------------------
    extra = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # -------------------------------------------------
    # DATABASE OPTIMIZATION
    # -------------------------------------------------
    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["device_id", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        # Show human-readable text first
        if self.description:
            return self.description
        return f"{self.created_at} {self.username} {self.action}"
