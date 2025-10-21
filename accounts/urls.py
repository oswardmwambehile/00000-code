from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserProfileView,
    UserRegistrationAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserInfoAPIView,
    ChangePasswordView,
    UpdateProfileView,
   UserListView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    
)
from . import views
urlpatterns = [
   
    path("user/profile/", UserProfileView.as_view(), name="user-profile"),
    path("user/", UserInfoAPIView.as_view(), name="user-info"),
    path("register/", UserRegistrationAPIView.as_view(), name="register-user"),
    path('users-lists/', UserListView.as_view(), name='user-list'),
    path('users-details/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users-update/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('users-delete/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path("login/", UserLoginAPIView.as_view(), name="login-user"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout-user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    
    path("user/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("user/update-profile/", UpdateProfileView.as_view(), name="update-profile"),

    path('branches/', views.branch_list, name='branch-list'),
    path('branches/create/', views.branch_create, name='branch-create'),
    path('branches/<int:pk>/', views.branch_detail, name='branch-detail'),
    path('branches/<int:pk>/update/', views.branch_update, name='branch-update'),
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch-delete'),
]
