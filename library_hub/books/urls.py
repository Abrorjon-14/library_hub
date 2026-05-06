from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/read/', views.book_read, name='book_read'),
    path('<int:pk>/save-progress/', views.save_reading_progress, name='save_reading_progress'),
]
