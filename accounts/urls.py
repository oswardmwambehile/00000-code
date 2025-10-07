from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserProfileView,
    UserRegistrationAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserInfoAPIView,
    ChangePasswordView,
    UpdateProfileView
)

urlpatterns = [
    # User profile and info
    path("user/profile/", UserProfileView.as_view(), name="user-profile"),
    path("user/", UserInfoAPIView.as_view(), name="user-info"),

    # Authentication
    path("register/", UserRegistrationAPIView.as_view(), name="register-user"),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # User settings
    path("user/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("user/update-profile/", UpdateProfileView.as_view(), name="update-profile"),
]
