
from django.urls import path
from . import views

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),

    # User Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # User Pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),

    # Pickup Requests
    path('pickup/', views.create_pickup, name='create_pickup'),
    path('my-pickups/', views.my_pickups, name='my_pickups'),

    # Recycler Pages
    path(
        'recycler-dashboard/',
        views.recycler_dashboard,
        name='recycler_dashboard'
    ),
    path(
        'recycler-register/',
        views.recycler_register,
        name='recycler_register'
    ),

    # Digital Certificate
    path(
        'certificate/<int:pickup_id>/',
        views.download_certificate,
        name='download_certificate'
    ),

    # Pickup Review
    path(
        'review/<int:pickup_id>/',
        views.submit_review,
        name='submit_review'
    ),
]
