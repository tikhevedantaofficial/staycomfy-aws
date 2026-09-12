"""
Django management command to send welcome emails to guests checking in today
Usage: python manage.py send_welcome_emails
"""
from django.core.management.base import BaseCommand
from bookings.email_service import send_welcome_emails_for_checkins
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send welcome emails to all guests checking in today'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Run without actually sending emails (for testing)',
        )
        parser.add_argument(
            '--test-email',
            type=str,
            dest='test_email',
            help='Send a test email to the specified address',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting welcome email sending process...')

        if options['test_email']:
            # Send test email
            self.stdout.write(f'📧 Sending test email to {options["test_email"]}...')
            from bookings.email_service import SNSEmailService
            email_service = SNSEmailService()
            success = email_service.send_test_email(options['test_email'])
            
            if success:
                self.stdout.write(self.style.SUCCESS('✅ Test email sent successfully!'))
            else:
                self.stdout.write(self.style.ERROR('❌ Failed to send test email'))
            return

        if options['dry_run']:
            # Dry run - just show what would be sent
            from bookings.email_service import get_checkin_bookings
            bookings = get_checkin_bookings()
            
            self.stdout.write(f'📋 Dry run mode - would send {bookings.count()} welcome emails:')
            for booking in bookings:
                self.stdout.write(f'  - {booking.user.email} for {booking.hotel.name} (Check-in: {booking.check_in})')
            
            self.stdout.write(self.style.WARNING('⚠️  Dry run completed - no emails were actually sent'))
            return

        # Actual email sending
        results = send_welcome_emails_for_checkins()
        
        self.stdout.write(f'📊 Email sending completed:')
        self.stdout.write(f'  Total bookings processed: {results["total"]}')
        self.stdout.write(f'  Emails sent successfully: {results["sent"]}')
        self.stdout.write(f'  Emails failed: {results["failed"]}')
        
        if results['errors']:
            self.stdout.write(self.style.ERROR('❌ Errors encountered:'))
            for error in results['errors']:
                self.stdout.write(f'  - {error}')
        
        if results['sent'] > 0:
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully sent {results["sent"]} welcome emails!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  No welcome emails were sent'))
        
        self.stdout.write('🏁 Welcome email sending process completed')