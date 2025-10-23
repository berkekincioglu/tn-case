from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_reservation_confirmation_email(reservation):
    """Send confirmation email to passenger after reservation is created."""
    subject = f'Flight Reservation Confirmation - {reservation.reservation_code}'
    flight = reservation.flight
    airplane = flight.airplane

    message = f"""
Dear {reservation.passenger_name},

Thank you for booking with us! Your flight reservation has been confirmed.

RESERVATION DETAILS
-------------------
Reservation Code: {reservation.reservation_code}
Status: {'Active' if reservation.status else 'Cancelled'}

FLIGHT INFORMATION
------------------
Flight Number: {flight.flight_number}
Departure: {flight.departure}
Destination: {flight.destination}
Departure Time: {flight.departure_time.strftime('%B %d, %Y at %I:%M %p')}
Arrival Time: {flight.arrival_time.strftime('%B %d, %Y at %I:%M %p')}

AIRCRAFT DETAILS
----------------
Aircraft: {airplane.model}
Tail Number: {airplane.tail_number}

IMPORTANT INFORMATION
---------------------
- Please arrive at the airport at least 2 hours before departure
- Bring a valid ID and your reservation code: {reservation.reservation_code}
- Check-in opens 24 hours before departure

Thank you for choosing our airline!

Best regards,
Airline Management Team
    """.strip()

    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@airline.com'

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[reservation.passenger_email],
            fail_silently=False,
        )
        logger.info(f'Confirmation email sent to {reservation.passenger_email}')
        return True

    except Exception as e:
        logger.error(f'Failed to send confirmation email: {e}')
        return False


def send_cancellation_email(reservation):
    """Send cancellation confirmation email to passenger."""
    subject = f'Reservation Cancelled - {reservation.reservation_code}'
    flight = reservation.flight

    message = f"""
Dear {reservation.passenger_name},

Your flight reservation has been cancelled as requested.

CANCELLED RESERVATION
---------------------
Reservation Code: {reservation.reservation_code}
Flight Number: {flight.flight_number}
Route: {flight.departure} → {flight.destination}
Departure Time: {flight.departure_time.strftime('%B %d, %Y at %I:%M %p')}

If you did not request this cancellation, please contact us immediately.

Thank you for your understanding.

Best regards,
Airline Management Team
    """.strip()

    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@airline.com'

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[reservation.passenger_email],
            fail_silently=False,
        )
        logger.info(f'Cancellation email sent to {reservation.passenger_email}')
        return True

    except Exception as e:
        logger.error(f'Failed to send cancellation email: {e}')
        return False
