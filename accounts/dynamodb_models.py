"""
DynamoDB models for Accounts app
These models provide a DynamoDB-based alternative to the SQL models
"""
import uuid
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from config.dynamodb_utils import dynamodb_manager

class CustomUser:
    """DynamoDB CustomUser model"""
    
    def __init__(self, email=None, first_name='', last_name='', 
                 password=None, is_staff=False, is_active=True, 
                 date_joined=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.is_staff = is_staff
        self.is_active = is_active
        self.date_joined = date_joined or datetime.utcnow()
    
    def save(self):
        """Save user to DynamoDB"""
        item = {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': self.password,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'date_joined': self.date_joined
        }
        dynamodb_manager.put_item('users', item)
    
    def delete(self):
        """Delete user from DynamoDB"""
        dynamodb_manager.delete_item('users', {'email': self.email})
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password matches"""
        return check_password(raw_password, self.password)
    
    @classmethod
    def get(cls, email):
        """Get user by email"""
        item = dynamodb_manager.get_item('users', {'email': email})
        if item:
            return cls(**item)
        return None
    
    @classmethod
    def all(cls):
        """Get all users"""
        items = dynamodb_manager.scan_table('users')
        return [cls(**item) for item in items]
    
    @classmethod
    def create_user(cls, email, password=None, **extra_fields):
        """Create a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = email.lower()
        user = cls(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    @classmethod
    def create_superuser(cls, email, password=None, **extra_fields):
        """Create a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        return cls.create_user(email, password, **extra_fields)
    
    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for authenticated users"""
        return False
    
    def get_full_name(self):
        """Get the user's full name"""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        """Get the user's short name"""
        return self.first_name
    
    def to_dict(self):
        """Convert to dictionary (excluding password)"""
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'full_name': self.get_full_name()
        }
    
    def __str__(self):
        return self.email


class CustomUserManager:
    """Manager for DynamoDB CustomUser operations"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create a regular user"""
        return CustomUser.create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create a superuser"""
        return CustomUser.create_superuser(email, password, **extra_fields)
    
    def get_by_email(self, email):
        """Get user by email"""
        return CustomUser.get(email)
    
    def all(self):
        """Get all users"""
        return CustomUser.all()