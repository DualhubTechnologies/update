from django.urls import path
# from accounts.views import login_view, logout_view
# from accounts.views import create_user_view
# from accounts.views import create_user_view, dashboard_view
from accounts.views_auth import force_password_change
from django.contrib.auth import views as auth_views
from accounts.views_superadmin  import  superadmin_dashboard
from accounts.views_auth import user_login,  logout_view
from accounts.views_staff_accounts import staff_accounts_page
from django.views.generic import RedirectView

app_name = "accounts"

urlpatterns = [
 path("login/", user_login, name="user_login"),
path("logout/", logout_view, name="logout"),

 path("force-password-change/", force_password_change, name="force_password_change"),
 path("superadmin/", superadmin_dashboard, name="superadmin_dashboard"),
 path("staff-accounts/", staff_accounts_page, name="staff_accounts_page"),



 
]
