from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.home, name='home'),
    path('my-bookings/', views.user_bookings, name='user_bookings'),
    path('cancel-booking/<uuid:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('properties', views.property_list, name='property_list'),
    path('add/', views.add_property, name='add_property'),
    path('properties/<uuid:property_id>/', views.property_detail, name='property_detail'),
    path('properties/<uuid:property_id>/book/', views.book_property, name='book_property'),
    path('properties/approve/<uuid:property_id>/', views.approve_property, name='approve_property'),
]