from django.contrib import admin
from .models import ParentGuardian

@admin.register(ParentGuardian)
class ParentAdmin(admin.ModelAdmin):
    list_display = (
        "student","name", "contact_number", "relationship",
    )
    list_filter = ("name", "contact_number", "relationship")
    search_fields = ("name", "contact_number", "relationship")
   

