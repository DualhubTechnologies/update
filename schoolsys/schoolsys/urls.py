"""
URL configuration for schoolsys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from accounts.views_auth import user_login
from django.conf import settings
from django.conf.urls.static import static



from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login, name='user_login'),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboards.urls")),
    path("calendar/", include("calendarapp.urls")),
    path("profile/", include("schoolprofile.urls")),
    path("teachers/", include("teachers.urls")),
    path("students/", include("students.urls")),
    path("", RedirectView.as_view(pattern_name="dashboards:user_dashboard", permanent=False)),
]
if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)