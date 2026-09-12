"""
AWS SNS Email Service for Staycomfy
Handles sending welcome emails to guests on their check-in day
"""
import boto3
import os
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date
import logging

logger = logging.getLogger(__name__)


class SNSEmailService:
    """Service for sending emails via AWS SNS"""
    
    def __init__(self):
        self.sns_client = boto3.client(
            'sns',
            region_name=getattr(settings, 'AWS_REGION', 'ap-south-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )
        self.topic_arn = getattr(settings, 'SNS_TOPIC_ARN', None)
    
    def send_welcome_email(self, booking):
        """
        Send welcome email to guest on check-in day
        
        Args:
            booking: Booking object with guest and hotel details
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Get user email
            recipient_email = booking.user.email
            
            # Prepare email content
            subject = f"Welcome to {booking.hotel.name}! Your Check-in Day has Arrived"
            
            # Render email template
            context = {
                'guest_name': booking.user.get_full_name() or booking.user.email.split('@')[0],
                'hotel_name': booking.hotel.name,
                'hotel_city': booking.hotel.city,
                'room_name': booking.room.name,
                'check_in': booking.check_in.strftime('%B %d, %Y'),
                'check_out': booking.check_out.strftime('%B %d, %Y'),
                'num_nights': booking.num_nights,
                'guests': booking.guests,
                'total_price': booking.total_price,
            }
            
            html_body = render_to_string('bookings/welcome_email.html', context)
            text_body = render_to_string('bookings/welcome_email.txt', context)
            
            # Send email via SNS
            if self.topic_arn:
                # Send via SNS topic (recommended for production)
                response = self.sns_client.publish(
                    TopicArn=self.topic_arn,
                    Message=text_body,
                    Subject=subject,
                    MessageStructure='html'
                )
            
            
            logger.info(f"Welcome email sent to {recipient_email} for booking {booking.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {recipient_email}: {str(e)}")
            return False
    
    def send_test_email(self, recipient_email):
        """Send a test email to verify SNS configuration"""
        try:
            subject = "Staycomfy - Test Email"
            message = """
           Test Email from Staycomfy
            
This is a test email to verify that your AWS SNS configuration is working correctly.

If you received this email, your SNS email service is properly configured!

Best regards,
Staycomfy Team"""
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject=subject,
                MessageStructure='html'
            )
            
            logger.info(f"Test email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False


def get_checkin_bookings():
    """
    Get all bookings that have check-in today and haven't received welcome email
    
    Returns:
        QuerySet: Bookings for today's check-ins
    """
    from .models import Booking
    
    today = timezone.now().date()
    
    return Booking.objects.filter(
        check_in=today,
        status='confirmed',
        welcome_email_sent=False
    )


def send_welcome_emails_for_checkins():
    """
    Send welcome emails to all guests checking in today
    
    Returns:
        dict: Summary of email sending results
    """
    bookings = get_checkin_bookings()
    email_service = SNSEmailService()
    
    results = {
        'total': bookings.count(),
        'sent': 0,
        'failed': 0,
        'errors': []
    }
    
    for booking in bookings:
        try:
            success = email_service.send_welcome_email(booking)
            if success:
                booking.welcome_email_sent = True
                booking.save()
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"Booking {booking.id}: Email send failed")
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Booking {booking.id}: {str(e)}")
            logger.error(f"Error processing booking {booking.id}: {str(e)}")
    
    logger.info(f"Welcome email sending completed: {results}")
    return results