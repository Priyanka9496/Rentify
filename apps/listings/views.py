from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
import json
from .forms import PropertyForm
from .models import Property, Booking
from .forms import BookingForm
from django.contrib.auth.decorators import user_passes_test
from apps.fraud.models import FraudActivity
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Property  # Ensure you import the necessary models


@staff_member_required(login_url='accounts:login')  # Ensures only staff can access this view
def approve_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    property.is_verified = True  # Mark property as verified
    property.save()
    messages.success(request, f"Property '{property.title}' has been approved and listed.")
    return redirect('listings:property_list')


def home(request):
    properties = Property.objects.filter(is_verified=True)
    return render(request, 'listings/home.html', {'properties': properties})


@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'listings/user_bookings.html', {'bookings': bookings})


def property_list(request):
    properties = Property.objects.filter(is_verified=True)  # Display only verified properties
    return render(request, 'listings/property_list.html', {'properties': properties})


def detect_fraud(user, booking):
    """Enhanced Fraud Detection Logic"""
    reasons = []

    # Rule 1: Multiple bookings within the last 10 minutes
    recent_bookings = Booking.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(minutes=10)
    ).count()

    print(f"Recent bookings count for {user.username}: {recent_bookings}")

    if recent_bookings > 3:
        reasons.append("Multiple bookings within a short time frame.")

    # Rule 2: Check for blacklisted email domains
    blacklist_domains = ["fraudmail.com", "scammer.net"]
    if any(domain in user.email for domain in blacklist_domains):
        reasons.append("Blacklisted email domain detected.")

    # Rule 3: Location mismatch (as an example)
    if "New York" not in booking.property.address:
        reasons.append("Location mismatch detected.")

    # Log and notify about fraud
    for reason in reasons:
        FraudActivity.objects.create(user=user, booking_id=booking.id, reason=reason)

    return reasons


@login_required(login_url='accounts:login')
def book_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    bookings = Booking.objects.filter(property=property)
    booked_dates = [
        date.strftime('%Y-%m-%d')
        for booking in bookings
        for date in (booking.start_date + timedelta(days=i)
                     for i in range((booking.end_date - booking.start_date).days + 1))
    ]
    booked_dates_json = json.dumps(booked_dates)

    form = BookingForm()

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Check for overlapping bookings
            overlapping_booking = Booking.objects.filter(
                property=property,
                start_date__lt=end_date,
                end_date__gt=start_date
            ).exists()

            if overlapping_booking:
                messages.error(request, "This property is already booked for the selected dates.")
                return redirect('listings:book_property', property_id=property.id)

            # TEMPORARY booking object (not saved)
            booking = form.save(commit=False)
            booking.user = request.user
            booking.property = property

            # Run fraud check
            fraud_reasons = detect_fraud(request.user, booking)

            if fraud_reasons:
                messages.warning(request, f"⚠️ Potential fraud detected: {', '.join(fraud_reasons)}")
                messages.error(request, f"Booking flagged as fraudulent due to: {', '.join(fraud_reasons)}")

                send_mail(
                    'Fraudulent Booking Attempt Detected',
                    f'User: {request.user.email}\nReasons: {", ".join(fraud_reasons)}',
                    'admin@propertylistings.com',
                    ['admin@propertylistings.com'],
                    fail_silently=True,
                )
                return redirect('listings:property_list')

            # ✅ Save booking data temporarily in session
            request.session['pending_booking'] = {
                'property_id': str(property.id),
                'start_date': str(start_date),
                'end_date': str(end_date),
            }

            return redirect('payments:confirm_payment')  # No booking.id passed anymore!

    return render(request, 'listings/book_property.html', {
        'form': form,
        'property': property,
        'booked_dates_json': booked_dates_json
    })


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
    else:
        messages.error(request, "Invalid request method.")

    return redirect('listings:user_bookings')


def is_verified_user(user):
    return user.groups.filter(name='verified').exists()


@login_required(login_url='accounts:login')
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = request.user
            property_instance.is_verified = False
            property_instance.save()

            messages.success(request, "Property submitted for review. It will be listed once approved.")
            return redirect('listings:property_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm(user=request.user)

    return render(request, 'listings/add_property.html', {'form': form})


@login_required(login_url='accounts:login')
def property_detail(request, property_id):
    """
    Displays detailed information for a single property.
    """
    property_instance = get_object_or_404(Property, id=property_id)

    # Optional: Restrict access if the property isn't verified
    if not property_instance.is_verified and not request.user.is_superuser:
        return render(request, 'listings/access_denied.html', {
            'message': "You don't have permission to view this unverified property."
        })

    return render(request, 'listings/property_detail.html', {
        'property': property_instance
    })