from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "username",
        "description",
        "method",
        "status_code",
        "path",
    )

    list_filter = ("action", "method", "app_label", "model")
    search_fields = ("description", "username", "path", "object_repr")
    readonly_fields = [field.name for field in ActivityLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
