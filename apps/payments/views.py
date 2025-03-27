from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from apps.listings.models import Booking
from ..listings.models import Booking
from .models import Payment
from .forms import CreditCardForm
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..listings.models import Property
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
@login_required
def create_checkout_session(request):
    data = request.session.get('pending_booking')
    if not data:
        return JsonResponse({'error': 'No booking in session'}, status=400)
    property = get_object_or_404(Property, id=data['property_id'])
    amount = int(property.price_per_night * 100)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Booking for {property.title}',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payments:stripe_success')),
            cancel_url=request.build_absolute_uri(reverse('payments:stripe_cancel')),
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required
def stripe_success(request):
    data = request.session.pop('pending_booking', None)
    if not data:
        messages.error(request, "No booking data found in session.")
        return redirect('listings:property_list')

    # Get property
    property = get_object_or_404(Property, id=data['property_id'])

    # Create the booking after successful payment
    booking = Booking.objects.create(
        user=request.user,
        property=property,
        start_date=data['start_date'],
        end_date=data['end_date']
    )

    # Create the payment
    Payment.objects.create(
        user=request.user,
        booking=booking,
        amount=booking.property.price_per_night,
        payment_method='stripe',
        status='completed'
    )
    messages.success(request, "✅ Stripe payment successful. Booking confirmed!")
    return redirect('payments:payment_success')


@login_required
def stripe_cancel(request, booking_id):
    request.session.pop('pending_booking', None)
    messages.warning(request, "⚠️ Stripe payment was cancelled. No booking was made.")
    return redirect('listings:property_list')


# @login_required
# def make_payment(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id)
#
#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             payment = form.save(commit=False)
#             payment.user = request.user
#             payment.booking = booking
#             payment.amount = booking.property.price_per_night  # Assume 1-night booking for simplicity
#             payment.status = 'pending'  # Initially mark it as pending
#             payment.save()
#
#             messages.success(request, "Payment is pending. Please verify through payment gateway.")
#             return redirect('listings:property_list')
#     else:
#         form = PaymentForm()
#
#     return render(request, 'payments/payment_success.html', {'form': form, 'booking': booking})


@login_required
def confirm_payment(request):
    data = request.session.get('pending_booking')
    if not data:
        messages.error(request, "No pending booking found.")
        return redirect('listings:property_list')

    selected_property = get_object_or_404(Property, id=data['property_id'])

    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            booking = Booking.objects.create(
                user=request.user,
                property=selected_property,
                start_date=data['start_date'],
                end_date=data['end_date']
            )
            # Simulate payment processing (replace with real gateway later)
            Payment.objects.create(
                user=request.user,
                booking=booking,
                amount=selected_property.price_per_night,
                payment_method='credit_card',
                status='completed'
            )
            # Clear session
            del request.session['pending_booking']

            messages.success(request, "✅ Payment completed and booking confirmed!")
            return redirect('payments:payment_success')
        else:
            print("Payment Form Errors:", form.errors)
    else:
        form = CreditCardForm()

    return render(
        request, 'payments/confirm_payment.html', {
            'form': form,
            'property': selected_property,
            'price': selected_property.price_per_night,
            'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
        })


@login_required
def payment_success(request):
    latest_payment = Payment.objects.filter(user=request.user).latest('created_at')
    return render(request, 'payments/payment_success.html', {'booking': latest_payment.booking})