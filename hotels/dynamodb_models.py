"""
DynamoDB models for Hotels app
These models provide a DynamoDB-based alternative to the SQL models
"""
import uuid
from decimal import Decimal
from datetime import datetime
from config.dynamodb_utils import dynamodb_manager

class Hotel:
    """DynamoDB Hotel model"""
    
    def __init__(self, id=None, name=None, city=None, description=None, 
                 image=None, rating=0.0, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.city = city
        self.description = description
        self.image = image
        self.rating = Decimal(str(rating))
        self.created_at = created_at or datetime.utcnow()
    
    def save(self):
        """Save hotel to DynamoDB"""
        item = {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'description': self.description,
            'rating': self.rating,
            'created_at': self.created_at
        }
        if self.image:
            item['image'] = self.image
        
        dynamodb_manager.put_item('hotels', item)
    
    def delete(self):
        """Delete hotel from DynamoDB"""
        dynamodb_manager.delete_item('hotels', {'id': self.id})
    
    @classmethod
    def get(cls, hotel_id):
        """Get hotel by ID"""
        item = dynamodb_manager.get_item('hotels', {'id': hotel_id})
        if item:
            return cls(**item)
        return None
    
    @classmethod
    def all(cls):
        """Get all hotels"""
        items = dynamodb_manager.scan_table('hotels')
        return [cls(**item) for item in items]
    
    @classmethod
    def filter_by_city(cls, city):
        """Filter hotels by city"""
        items = dynamodb_manager.scan_table('hotels', 'city = :city', {':city': city})
        return [cls(**item) for item in items]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'description': self.description,
            'image': self.image,
            'rating': float(self.rating),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __str__(self):
        return f"{self.name} — {self.city}"


class Room:
    """DynamoDB Room model"""
    
    def __init__(self, id=None, hotel_id=None, name=None, description=None,
                 price_per_night=None, capacity=2, image=None):
        self.id = id or str(uuid.uuid4())
        self.hotel_id = hotel_id
        self.name = name
        self.description = description
        self.price_per_night = Decimal(str(price_per_night)) if price_per_night else Decimal('0.00')
        self.capacity = capacity
        self.image = image
    
    def save(self):
        """Save room to DynamoDB"""
        item = {
            'id': self.id,
            'hotel_id': self.hotel_id,
            'name': self.name,
            'description': self.description,
            'price_per_night': self.price_per_night,
            'capacity': self.capacity
        }
        if self.image:
            item['image'] = self.image
        
        dynamodb_manager.put_item('rooms', item)
    
    def delete(self):
        """Delete room from DynamoDB"""
        dynamodb_manager.delete_item('rooms', {'id': self.id, 'hotel_id': self.hotel_id})
    
    @classmethod
    def get(cls, room_id, hotel_id):
        """Get room by ID and hotel_id"""
        item = dynamodb_manager.get_item('rooms', {'id': room_id, 'hotel_id': hotel_id})
        if item:
            return cls(**item)
        return None
    
    @classmethod
    def all(cls):
        """Get all rooms"""
        items = dynamodb_manager.scan_table('rooms')
        return [cls(**item) for item in items]
    
    @classmethod
    def filter_by_hotel(cls, hotel_id):
        """Filter rooms by hotel using GSI"""
        items = dynamodb_manager.query_table(
            'rooms',
            'hotel_id = :hotel_id',
            index_name='hotel-id-index'
        )
        return [cls(**item) for item in items]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'hotel_id': self.hotel_id,
            'name': self.name,
            'description': self.description,
            'price_per_night': float(self.price_per_night),
            'capacity': self.capacity,
            'image': self.image
        }
    
    def __str__(self):
        return f"{self.name} @ Hotel {self.hotel_id}"