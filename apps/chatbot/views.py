from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Chat
import json
from django.views.decorators.csrf import csrf_exempt
from .openai_api import ask_openai


@csrf_exempt
def chatbot_ui(request):
    """Render Chatbot UI with previous chat history."""
    chats = Chat.objects.filter(user=request.user).order_by('created_at')
    response = None

    if request.method == 'POST':
        message = request.POST.get('message')
        print("message: ",message)

        # ✅ Validate for empty message
        if not message:
            response = "Message cannot be empty."
        else:
            response = get_local_response(message)
            if not response:
                response = ask_openai(message)
            response = ask_openai(message)
            print("response: ", response)

            # ✅ Save only if message and response are valid
            if message and response:
                Chat.objects.create(
                    user=request.user,
                    message=message,
                    response=response,
                    created_at=timezone.now()
                )

    return render(request, 'chatbot/chatbot.html', {'chats': chats, 'response': response})


@csrf_exempt
def chatbot_api(request):
    """Handle chatbot API responses for AJAX calls."""
    if request.method == 'POST':
        try:
            # Log the raw request body for debugging
            print("Raw Request Body:", request.body)

            # Decode the incoming JSON data
            data = json.loads(request.body)
            message = data.get('message')

            print("Extracted Message:", message)

            if not message:
                return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

            # Mock response for now
            local_response = get_local_response(message)
            if local_response:
                return JsonResponse({'message': message, 'response': local_response})

            response = ask_openai(message)
            return JsonResponse({'message': message, 'response': response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

    return JsonResponse({'error': 'Invalid request.'}, status=400)


def get_local_response(message):
    message = message.lower()

    if any(keyword in message for keyword in ["cancel", "cancel booking", "cancel reservation", "cancel my ticket"]):
        return (
            "Sorry to hear you have to cancel your booking. "
            "Before canceling, please note that 5% of the payment will be deducted as a cancellation charge. "
            "Do you still want to proceed?"
        )

    if "reschedule" in message:
        return "Sure, I can help you reschedule your booking. Please provide the new date and time."

    if message in ["hi", "hello", "hey"]:
        return "Hi there! How can I assist you today?"
    if "refund" in message and "policy" in message:
        return (
            "Our refund policy states that cancellations made within 24 hours of booking are fully refundable. "
            "After that, a 5% cancellation charge applies."
        )

        # 4. Booking Time / Details
    if any(keyword in message for keyword in ["what time", "booking time", "when is my booking",'booking']):
        return (
            "To check your booking time and details, please visit your profile or booking history section."
        )

        # 5. Payment Status
    if "payment" in message and "status" in message:
        return "To check your payment status, go to the payment section in your account dashboard."

    if "thank" in message:
        return "You're welcome! Let me know if there's anything else I can help with."

    # 8. Support / Contact
    if any(keyword in message for keyword in
            ["help", "support", "contact", "talk to agent", "customer service", "call you"]):
        return (
            "You can reach our support team via the Help section in your profile or by calling our support hotline. "
            "Is there anything specific you need help with?"
            "or you can direct call to support on +18709383090"
        )

    # 9. Confirmation / Booking Status
    if any(keyword in message for keyword in
            ["confirm", "confirmation", "confirmed", "booking status", "is it approved"]):
        return (
                "You can view your booking confirmation and status in your account under 'My Bookings'. "
                "Let me know if you need help finding it!"
        )

    return None  # No local match