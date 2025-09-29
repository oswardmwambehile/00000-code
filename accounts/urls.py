from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('add-visit/', views.add_visit, name='add_visit'),
    path('logout/', views.logout_user, name='logout'),
]
