"""
DynamoDB utilities for Django models
Provides a simple interface for DynamoDB operations using boto3
"""
import boto3
import os
from django.conf import settings
from decimal import Decimal
import json
from datetime import datetime

class DynamoDBManager:
    """Manager class for DynamoDB operations"""
    
    def __init__(self):
        self.resource = boto3.resource(
            'dynamodb',
            region_name=getattr(settings, 'AWS_REGION', 'ap-south-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )
        self.client = boto3.client(
            'dynamodb',
            region_name=getattr(settings, 'AWS_REGION', 'ap-south-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )
        self.table_prefix = getattr(settings, 'DYNAMODB_TABLE_PREFIX', 'staycomfy-')
    
    def get_table(self, table_name):
        """Get a DynamoDB table object"""
        full_table_name = f"{self.table_prefix}{table_name}"
        return self.resource.Table(full_table_name)
    
    def item_to_dict(self, item):
        """Convert DynamoDB item to regular dictionary"""
        return {k: self._deserialize_value(v) for k, v in item.items()}
    
    def _deserialize_value(self, value):
        """Deserialize DynamoDB value to Python type"""
        if 'S' in value:
            return value['S']
        elif 'N' in value:
            return Decimal(value['N'])
        elif 'B' in value:
            return value['B'].value
        elif 'SS' in value:
            return set(value['SS'])
        elif 'NS' in value:
            return set(Decimal(n) for n in value['NS'])
        elif 'BS' in value:
            return set(value['BS'])
        elif 'M' in value:
            return {k: self._deserialize_value(v) for k, v in value['M'].items()}
        elif 'L' in value:
            return [self._deserialize_value(v) for v in value['L']]
        elif 'NULL' in value:
            return None
        elif 'BOOL' in value:
            return value['BOOL']
        else:
            return value
    
    def dict_to_item(self, data):
        """Convert Python dictionary to DynamoDB item format"""
        return {k: self._serialize_value(v) for k, v in data.items()}
    
    def _serialize_value(self, value):
        """Serialize Python value to DynamoDB format"""
        if value is None:
            return {'NULL': True}
        elif isinstance(value, bool):
            return {'BOOL': value}
        elif isinstance(value, (int, float, Decimal)):
            return {'N': str(value)}
        elif isinstance(value, str):
            return {'S': value}
        elif isinstance(value, (set, list)):
            if isinstance(value, set):
                if all(isinstance(x, (int, float, Decimal)) for x in value):
                    return {'NS': [str(x) for x in value]}
                elif all(isinstance(x, str) for x in value):
                    return {'SS': list(value)}
                else:
                    return {'BS': [x.encode('utf-8') for x in value]}
            else:
                return {'L': [self._serialize_value(x) for x in value]}
        elif isinstance(value, dict):
            return {'M': {k: self._serialize_value(v) for k, v in value.items()}}
        elif isinstance(value, datetime):
            return {'S': value.isoformat()}
        elif hasattr(value, 'read'):  # File-like object
            return {'B': value.read()}
        else:
            return {'S': str(value)}
    
    def put_item(self, table_name, item):
        """Put an item into DynamoDB table"""
        table = self.get_table(table_name)
        table.put_item(Item=self.dict_to_item(item))
    
    def get_item(self, table_name, key):
        """Get an item from DynamoDB table by key"""
        table = self.get_table(table_name)
        response = table.get_item(Key=self.dict_to_item(key))
        if 'Item' in response:
            return self.item_to_dict(response['Item'])
        return None
    
    def update_item(self, table_name, key, update_expression, expression_values):
        """Update an item in DynamoDB table"""
        table = self.get_table(table_name)
        table.update_item(
            Key=self.dict_to_item(key),
            UpdateExpression=update_expression,
            ExpressionAttributeValues=self.dict_to_item(expression_values)
        )
    
    def delete_item(self, table_name, key):
        """Delete an item from DynamoDB table"""
        table = self.get_table(table_name)
        table.delete_item(Key=self.dict_to_item(key))
    
    def scan_table(self, table_name, filter_expression=None, expression_values=None):
        """Scan a DynamoDB table"""
        table = self.get_table(table_name)
        kwargs = {}
        if filter_expression:
            kwargs['FilterExpression'] = filter_expression
        if expression_values:
            kwargs['ExpressionAttributeValues'] = self.dict_to_item(expression_values)
        
        response = table.scan(**kwargs)
        items = [self.item_to_dict(item) for item in response.get('Items', [])]
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = table.scan(**kwargs)
            items.extend([self.item_to_dict(item) for item in response.get('Items', [])])
        
        return items
    
    def query_table(self, table_name, key_condition, index_name=None):
        """Query a DynamoDB table or index"""
        table = self.get_table(table_name)
        kwargs = {'KeyConditionExpression': key_condition}
        if index_name:
            kwargs['IndexName'] = index_name
        
        response = table.query(**kwargs)
        items = [self.item_to_dict(item) for item in response.get('Items', [])]
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = table.query(**kwargs)
            items.extend([self.item_to_dict(item) for item in response.get('Items', [])])
        
        return items

# Global DynamoDB manager instance
dynamodb_manager = DynamoDBManager()