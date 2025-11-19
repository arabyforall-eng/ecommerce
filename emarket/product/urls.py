
from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_all_products),
    path('products/new', views.new_product),
    path('products/<str:pk>/', views.get_by_id_product),
    path('products/update/<str:pk>/', views.update_product),
    path('products/delete/<str:pk>/', views.delete_product),

    path('<str:pk>/reviews', views.create_review),
    path('<str:pk>/reviews/delete', views.delete_review),
]
