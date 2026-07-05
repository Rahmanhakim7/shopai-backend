
from django.urls import path
from .views import (
    register, CustomTokenObtainPairView, profile, google_login, google_register, forgot_password, reset_password
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
]
