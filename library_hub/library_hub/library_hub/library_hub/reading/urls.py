from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_reading, name='my_reading'),
    path('progress/<int:book_id>/', views.save_progress, name='save_progress'),
    path('wishlist/<int:book_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
