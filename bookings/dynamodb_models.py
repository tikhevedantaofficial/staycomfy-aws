"""
DynamoDB models for Bookings app
These models provide a DynamoDB-based alternative to the SQL models
"""
import uuid
from decimal import Decimal
from datetime import datetime
from config.dynamodb_utils import dynamodb_manager

class Booking:
    """DynamoDB Booking model"""
    
    STATUS_CHOICES = ['confirmed', 'cancelled']
    
    def __init__(self, id=None, user_email=None, hotel_id=None, room_id=None,
                 check_in=None, check_out=None, guests=1, total_price=None,
                 status='confirmed', created_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_email = user_email
        self.hotel_id = hotel_id
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        self.guests = guests
        self.total_price = Decimal(str(total_price)) if total_price else Decimal('0.00')
        self.status = status
        self.created_at = created_at or datetime.utcnow()
    
    def save(self):
        """Save booking to DynamoDB"""
        item = {
            'id': self.id,
            'user_email': self.user_email,
            'hotel_id': self.hotel_id,
            'room_id': self.room_id,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'guests': self.guests,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at
        }
        dynamodb_manager.put_item('bookings', item)
    
    def delete(self):
        """Delete booking from DynamoDB"""
        dynamodb_manager.delete_item('bookings', {'id': self.id, 'user_email': self.user_email})
    
    @classmethod
    def get(cls, booking_id, user_email):
        """Get booking by ID and user_email"""
        item = dynamodb_manager.get_item('bookings', {'id': booking_id, 'user_email': user_email})
        if item:
            return cls(**item)
        return None
    
    @classmethod
    def all(cls):
        """Get all bookings"""
        items = dynamodb_manager.scan_table('bookings')
        return [cls(**item) for item in items]
    
    @classmethod
    def filter_by_user(cls, user_email):
        """Filter bookings by user using GSI"""
        items = dynamodb_manager.query_table(
            'bookings',
            'user_email = :user_email',
            index_name='user-email-index'
        )
        return [cls(**item) for item in items]
    
    @classmethod
    def filter_by_status(cls, status):
        """Filter bookings by status"""
        items = dynamodb_manager.scan_table('bookings', 'status = :status', {':status': status})
        return [cls(**item) for item in items]
    
    @classmethod
    def filter_by_room_and_dates(cls, room_id, check_in, check_out):
        """Filter bookings by room and date range for availability checking"""
        # This is a complex query - we'll need to scan and filter in Python
        # In production, consider using a different data model or GSI
        items = dynamodb_manager.scan_table('bookings')
        filtered = []
        for item in items:
            if (item['room_id'] == room_id and 
                item['status'] == 'confirmed' and
                not (item['check_out'] <= check_in or item['check_in'] >= check_out)):
                filtered.append(cls(**item))
        return filtered
    
    def cancel(self):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.save()
    
    @property
    def num_nights(self):
        """Calculate number of nights"""
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0
    
    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        return self.status == 'confirmed'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_email': self.user_email,
            'hotel_id': self.hotel_id,
            'room_id': self.room_id,
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'guests': self.guests,
            'total_price': float(self.total_price),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'num_nights': self.num_nights,
            'can_cancel': self.can_cancel
        }
    
    def __str__(self):
        return f"{self.user_email} — Room {self.room_id} @ Hotel {self.hotel_id}"