from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from hotels.models import Hotel, Room
from bookings.models import Booking

User = get_user_model()


class BaseTestCase(TestCase):
    """Shared setup for all tests."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123!',
            first_name='Test',
            last_name='User',
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123!',
        )
        self.hotel = Hotel.objects.create(
            name='Test Hotel',
            city='Test City',
            description='A great hotel.',
            rating=Decimal('4.5'),
        )
        self.room = Room.objects.create(
            hotel=self.hotel,
            name='Standard Room',
            description='A nice room.',
            price_per_night=Decimal('100.00'),
            capacity=3,
        )


class SignupTests(BaseTestCase):
    def test_signup_page_loads(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Join Staycomfy')

    def test_signup_success(self):
        response = self.client.post(reverse('signup'), {
            'email': 'newuser@example.com',
            'password': 'securePass123!',
            'password_confirm': 'securePass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_signup_duplicate_email(self):
        response = self.client.post(reverse('signup'), {
            'email': 'testuser@example.com',
            'password': 'securePass123!',
            'password_confirm': 'securePass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')

    def test_signup_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'email': 'new@example.com',
            'password': 'securePass123!',
            'password_confirm': 'different!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'do not match')


class LoginTests(BaseTestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'testpass123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password')


class HotelPageTests(BaseTestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staycomfy')

    def test_home_shows_hotels(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Hotel')

    def test_hotel_detail_page(self):
        response = self.client.get(reverse('hotel_detail', args=[self.hotel.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hotel')
        self.assertContains(response, 'Standard Room')

    def test_hotel_detail_404(self):
        response = self.client.get(reverse('hotel_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class BookingTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(email='testuser@example.com', password='testpass123!')

    def test_booking_page_loads(self):
        response = self.client.get(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Your Booking')

    def test_booking_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_create_booking_success(self):
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=4)
        response = self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': tomorrow.isoformat(),
                'check_out': day_after.isoformat(),
                'guests': 2,
            },
        )
        self.assertEqual(response.status_code, 302)
        booking = Booking.objects.filter(user=self.user).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(booking.guests, 2)
        # 3 nights * 100.00 = 300.00
        self.assertEqual(booking.total_price, Decimal('300.00'))

    def test_total_price_calculation(self):
        tomorrow = date.today() + timedelta(days=1)
        checkout = date.today() + timedelta(days=6)
        self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': tomorrow.isoformat(),
                'check_out': checkout.isoformat(),
                'guests': 1,
            },
        )
        booking = Booking.objects.filter(user=self.user).first()
        # 5 nights * 100.00 = 500.00
        self.assertEqual(booking.total_price, Decimal('500.00'))
        self.assertEqual(booking.num_nights, 5)

    def test_check_in_past_rejected(self):
        past = date.today() - timedelta(days=5)
        future = date.today() + timedelta(days=1)
        response = self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': past.isoformat(),
                'check_out': future.isoformat(),
                'guests': 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot be in the past')

    def test_checkout_before_checkin_rejected(self):
        day1 = date.today() + timedelta(days=5)
        day2 = date.today() + timedelta(days=3)
        response = self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': day1.isoformat(),
                'check_out': day2.isoformat(),
                'guests': 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'must be after check-in')

    def test_capacity_exceeded_rejected(self):
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=3)
        response = self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': tomorrow.isoformat(),
                'check_out': day_after.isoformat(),
                'guests': 10,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'maximum of')

    def test_overlapping_booking_prevented(self):
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=5)
        # Create first booking
        Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room=self.room,
            check_in=tomorrow,
            check_out=day_after,
            guests=1,
            total_price=Decimal('400.00'),
            status='confirmed',
        )
        # Try overlapping booking
        overlap_in = date.today() + timedelta(days=2)
        overlap_out = date.today() + timedelta(days=6)
        response = self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': overlap_in.isoformat(),
                'check_out': overlap_out.isoformat(),
                'guests': 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not available')

    def test_cancelled_booking_does_not_block(self):
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=5)
        Booking.objects.create(
            user=self.other_user,
            hotel=self.hotel,
            room=self.room,
            check_in=tomorrow,
            check_out=day_after,
            guests=1,
            total_price=Decimal('400.00'),
            status='cancelled',
        )
        # Should succeed since the existing booking is cancelled
        response = self.client.post(
            reverse('create_booking', args=[self.hotel.pk, self.room.pk]),
            {
                'check_in': tomorrow.isoformat(),
                'check_out': day_after.isoformat(),
                'guests': 2,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Booking.objects.filter(user=self.user, status='confirmed').count(), 1
        )


class CancelBookingTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(email='testuser@example.com', password='testpass123!')
        self.booking = Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room=self.room,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=3),
            guests=2,
            total_price=Decimal('200.00'),
            status='confirmed',
        )

    def test_cancel_booking_success(self):
        response = self.client.post(reverse('cancel_booking', args=[self.booking.pk]))
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')

    def test_cancel_already_cancelled(self):
        self.booking.status = 'cancelled'
        self.booking.save()
        response = self.client.post(reverse('cancel_booking', args=[self.booking.pk]))
        self.assertEqual(response.status_code, 302)

    def test_cannot_cancel_other_users_booking(self):
        other_booking = Booking.objects.create(
            user=self.other_user,
            hotel=self.hotel,
            room=self.room,
            check_in=date.today() + timedelta(days=10),
            check_out=date.today() + timedelta(days=12),
            guests=1,
            total_price=Decimal('200.00'),
            status='confirmed',
        )
        response = self.client.post(reverse('cancel_booking', args=[other_booking.pk]))
        self.assertEqual(response.status_code, 302)
        other_booking.refresh_from_db()
        self.assertEqual(other_booking.status, 'confirmed')


class MyBookingsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(email='testuser@example.com', password='testpass123!')

    def test_my_bookings_page_loads(self):
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Bookings')

    def test_my_bookings_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_my_bookings_shows_user_bookings(self):
        Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room=self.room,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=3),
            guests=2,
            total_price=Decimal('200.00'),
            status='confirmed',
        )
        response = self.client.get(reverse('my_bookings'))
        self.assertContains(response, 'Test Hotel')
        self.assertContains(response, '$200.00')

    def test_my_bookings_does_not_show_other_users(self):
        Booking.objects.create(
            user=self.other_user,
            hotel=self.hotel,
            room=self.room,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=3),
            guests=1,
            total_price=Decimal('200.00'),
            status='confirmed',
        )
        response = self.client.get(reverse('my_bookings'))
        self.assertNotContains(response, 'other@example.com')
