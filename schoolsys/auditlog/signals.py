import sys

from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import ActivityLog
from .middleware import get_current_request, get_client_ip, user_identity


# =========================================================
# INTERNAL SAFETY CHECKS
# =========================================================
def auditlog_table_ready():
    """
    Prevent audit logging during migrations or before
    the auditlog_activitylog table exists.
    """
    if "migrate" in sys.argv or "makemigrations" in sys.argv:
        return False

    try:
        return "auditlog_activitylog" in connection.introspection.table_names()
    except Exception:
        return False


# =========================================================
# HUMAN-READABLE DESCRIPTION BUILDER
# =========================================================
def build_description(instance, action):
    """
    Converts technical actions like `model.update`
    into human-readable audit messages.
    """

    model = instance._meta.model_name

    # ---- STUDENT MODEL (CUSTOM TEXT) ----
    if model == "student":
        full_name = getattr(instance, "full_name", str(instance))

        if action == "model.create":
            return f"Registered new student {full_name}"

        if action == "model.update":
            return f"Updated student biodata of {full_name}"

        if action == "model.delete":
            return f"Deleted student record of {full_name}"

    # ---- DEFAULT FALLBACK (ALL OTHER MODELS) ----
    return f"{action.replace('.', ' ').title()} {instance}"


# =========================================================
# CORE LOGGER
# =========================================================
def _log_model_event(instance, action, created=False):
    # ---- HARD STOP DURING MIGRATIONS / BOOTSTRAP ----
    if not auditlog_table_ready():
        return

    request = get_current_request()

    user = None
    identity = ""
    device_id = ""
    ip = None
    ua = ""
    session_key = ""
    path = ""
    method = ""

    if request:
        user = request.user if request.user.is_authenticated else None
        identity = user_identity(user) if user else ""
        device_id = request.COOKIES.get("device_id", "")
        ip = get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")[:1000]
        session_key = getattr(request.session, "session_key", "") or ""
        path = request.path or ""
        method = request.method or ""

    meta = instance._meta
    description = build_description(instance, action)

    ActivityLog.objects.create(
        user=user,
        username=identity,
        action=action,
        description=description,
        path=path,
        method=method,
        status_code=None,
        device_id=device_id,
        ip_address=ip,
        user_agent=ua,
        session_key=session_key,
        app_label=meta.app_label,
        model=meta.model_name,
        object_id=str(getattr(instance, "pk", "")),
        object_repr=str(instance)[:255],
        extra={"created": created},
    )


# =========================================================
# POST SAVE SIGNAL
# =========================================================
@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    # Prevent infinite loop
    if sender is ActivityLog:
        return

    # Ignore Django system apps
    if sender._meta.app_label in (
        "admin",
        "auth",
        "sessions",
        "contenttypes",
    ):
        return

    action = "model.create" if created else "model.update"
    _log_model_event(instance, action=action, created=created)


# =========================================================
# POST DELETE SIGNAL
# =========================================================
@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender is ActivityLog:
        return

    if sender._meta.app_label in (
        "admin",
        "auth",
        "sessions",
        "contenttypes",
    ):
        return

    _log_model_event(instance, action="model.delete")
