from django.urls import path
from . import views

urlpatterns = [
    path('visits/new/<int:sale_id>/', views.new_visit, name='new_visit_for_sale'),
     path('my-visits/', views.user_visits, name='user_visits'),
      path('visit/<int:visit_id>/', views.visit_detail, name='visit_detail'),
    
]
