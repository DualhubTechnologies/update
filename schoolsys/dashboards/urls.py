from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import RedirectView

from .views import (students_gender_data, students_per_class_data, user_dashboard)


app_name = "dashboards"

urlpatterns = [
        # 1) THIS must exist (so "user_dashboard" can be reversed)
    path("dashboard/", user_dashboard, name="user_dashboard"),

    # 2) Redirect /accounts/  -> /accounts/dashboard/
    path("", RedirectView.as_view(pattern_name="dashboards:user_dashboard", permanent=False)),



    path("students-per-class/",students_per_class_data,name="students_per_class_data"),
    path("students-gender/",students_gender_data,name="students_gender_data"),

]    
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
