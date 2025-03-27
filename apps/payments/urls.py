from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payments/confirm/', views.confirm_payment, name='confirm_payment'),
    path('success/', views.payment_success, name='payment_success'),
    # Stripe
    path('stripe/create-session/', views.create_checkout_session, name='stripe_checkout_session'),
    path('stripe/success/', views.stripe_success, name='stripe_success'),
    path('stripe/cancel/', views.stripe_cancel, name='stripe_cancel'),
]
