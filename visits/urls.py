from django.urls import path
from . import views

urlpatterns = [
    path('visits/new/', views.new_visit, name='new_visit_for_sale'),
    path('my-visits/', views.user_visits, name='user_visits'),
    path('visit/<int:visit_id>/', views.visit_detail, name='visit_detail'),
    path('all_visits-list/', views.all_visit_list, name='all_visit_list'),
    path('user-visit/<int:pk>/update/', views.visit_update, name='visit_update'),
    path('get-contacts/<int:company_id>/', views.get_contacts, name='get_contacts'),
    path('get-contact-details/<int:contact_id>/', views.get_contact_details, name='get_contact_details'),
    
]
