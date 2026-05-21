from django.urls import path
from .views import (
    register, CustomTokenObtainPairView
)

urlpatterns = [
    path('register/', register),
    path(
        'token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    )
]
