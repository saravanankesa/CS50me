from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", auth_views.LoginView.as_view(template_name="auctions/login.html"), name="login"),  # Default route to login page
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing/', views.create_listing, name='create_listing'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('edit_listing/<int:pk>/', views.edit_listing, name='edit_listing'),
    path('delete_listing/<int:pk>/', views.delete_listing, name='delete_listing'),
]
