
from django.urls import path
from .views import (
    register, CustomTokenObtainPairView, profile, google_login, google_register, forgot_password, reset_password, admin_users, admin_deactivate_user,
    admin_activate_user
)

urlpatterns = [
    path('register/', register),
    path(
        'token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        "profile/",
        profile,
        name="profile"
    ),
    path(
        "google/login/",
        google_login,
        name="google_login",
    ),
    path(
        "google/register/",
        google_register,
        name="google_register",
    ),
    path(
        "forgot-password/",
        forgot_password,
        name="forgot_password",
    ),
    path(
        "reset-password/",
        reset_password,
        name="reset_password",
    ),
    path("admin/users/", admin_users, name="admin-users"),
    path(
        "admin/users/<int:user_id>/deactivate/",
        admin_deactivate_user,
        name="admin-deactivate-user",
    ),
    path(
        "admin/users/<int:user_id>/activate/",
        admin_activate_user,
        name="admin-activate-user",
    ),
]
