from django.urls import path
from . import views

urlpatterns = [
    path("product-lists", views.product_list, name="product-list"),
    path("<int:pk>/", views.product_detail, name="product-detail"),
    path("<int:pk>/delete/", views.product_delete, name="product-delete"),
]
