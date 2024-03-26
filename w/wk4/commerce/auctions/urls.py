from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing/', views.create_listing, name='create_listing'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('edit_listing/<int:pk>/', views.edit_listing, name='edit_listing'),
    path('delete_listing/<int:pk>/', views.delete_listing, name='delete_listing'),
]
