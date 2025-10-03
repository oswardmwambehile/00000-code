from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('add-visit/', views.add_visit, name='add_visit'),
    path('logout/', views.logout_user, name='logout'),
    path('users/', views.user_list, name='user_list'),
   path("branch-list/", views.branch_list, name="branch-list"),  # list + add + edit
    path("branch-detail/<int:pk>/", views.branch_detail, name="branch-detail"),
    path("branch-delete/<int:pk>/", views.branch_delete, name="branch-delete"),
     path('add_user/', views.register, name='register'),
    path('users-edit/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('change-password/', views.change_password, name='change_password'),
     path('adminchange-password/', views.adminchange_password, name='changes_password'),
     path('profile/', views.profile_view, name='profile'),
      path('admin-profile/', views.adminprofile_view, name='profiles'),
    path('users_disable/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
]
