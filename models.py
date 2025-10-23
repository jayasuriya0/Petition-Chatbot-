from pymongo import MongoClient
from datetime import datetime, UTC
import bcrypt
from config import Config
from bson import ObjectId

client = MongoClient(Config.MONGO_URI)
db = client.petition_system

class User:
    def __init__(self, name, email, phone, address, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.password = self.hash_password(password)
        self.email_verified = False
        self.otp = None
        self.otp_created_at = None
        self.created_at = datetime.now(UTC)
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def save(self):
        return db.users.insert_one({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'password': self.password,
            'email_verified': self.email_verified,
            'otp': self.otp,
            'otp_created_at': self.otp_created_at,
            'created_at': self.created_at
        })
    
    @staticmethod
    def find_by_email(email):
        return db.users.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        from bson import ObjectId
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            obj_id = user_id
        return db.users.find_one({'_id': obj_id})

class Department:
    def __init__(self, name, email, password, categories=None, profile=None, phone=None, address=None):
        self.name = name
        self.email = email
        self.password = self.hash_password(password)
        self.categories = categories or []
        self.profile = profile
        self.phone = phone
        self.address = address
        self.email_verified = False
        self.otp = None
        self.otp_created_at = None
        self.created_at = datetime.now(UTC)
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def save(self):
        return db.departments.insert_one({
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'categories': self.categories,
            'profile': self.profile,
            'phone': self.phone,
            'address': self.address,
            'email_verified': self.email_verified,
            'otp': self.otp,
            'otp_created_at': self.otp_created_at,
            'created_at': self.created_at
        })
    
    @staticmethod
    def find_by_email(email):
        return db.departments.find_one({'email': email})
    
    @staticmethod
    def find_all():
        return list(db.departments.find())

class Admin:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = self.hash_password(password)
        self.created_at = datetime.now(UTC)
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def save(self):
        return db.admins.insert_one({
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at
        })
    
    @staticmethod
    def find_by_email(email):
        return db.admins.find_one({'email': email})

class Petition:
    def __init__(self, user_id, title, category, department, description, location, 
                 urgency, full_name, email, phone, address, attachments=None):
        self.user_id = user_id
        self.title = title
        self.category = category
        self.department = department
        self.description = description
        self.location = location
        self.urgency = urgency
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.address = address
        self.attachments = attachments or []
        self.status = 'pending'
        self.rejection_reason = None  # New field for rejection reason
        self.ticket_id = self.generate_ticket_id()
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self.deadline = self.calculate_deadline(urgency)
    
    def generate_ticket_id(self):
        import random
        import string
        return 'PET-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def calculate_deadline(self, urgency):
        """Calculate deadline based on urgency level"""
        from datetime import timedelta
        now = datetime.now(UTC)
        
        # Urgency-based deadlines
        urgency_hours = {
            'critical': 24,    # 1 day
            'high': 72,        # 3 days
            'medium': 168,     # 7 days
            'low': 336         # 14 days
        }
        
        hours = urgency_hours.get(urgency.lower(), 168)  # default to 7 days
        return now + timedelta(hours=hours)
    
    def save(self):
        # Always store user_id as string
        return db.petitions.insert_one({
            'user_id': str(self.user_id),
            'title': self.title,
            'category': self.category,
            'department': self.department,
            'description': self.description,
            'location': self.location,
            'urgency': self.urgency,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'attachments': self.attachments,
            'status': self.status,
            'rejection_reason': self.rejection_reason,
            'ticket_id': self.ticket_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deadline': self.deadline
        })
    
    @staticmethod
    def find_by_user(user_id):
        try:
            # Always query user_id as string
            query = {'user_id': str(user_id)}
            cursor = db.petitions.find(query).sort('created_at', -1)
            petitions = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for petition in petitions:
                petition['_id'] = str(petition['_id'])
            
            return petitions
        except Exception as e:
            print(f'Error in find_by_user: {str(e)}')
            print(f'User ID: {user_id}')
            return []
    
    @staticmethod
    def find_by_ticket(ticket_id):
        try:
            petition = db.petitions.find_one({'ticket_id': ticket_id})
            if petition:
                # Convert ObjectId to string for JSON serialization
                if '_id' in petition:
                    petition['_id'] = str(petition['_id'])
                if 'user_id' in petition:
                    petition['user_id'] = str(petition['user_id'])
            return petition
        except Exception as e:
            print(f'Error in find_by_ticket: {str(e)}')
            return None
    
    @staticmethod
    def find_all():
        try:
            petitions = list(db.petitions.find().sort('created_at', -1))
            
            # Convert ObjectId to string for JSON serialization
            for petition in petitions:
                if '_id' in petition:
                    petition['_id'] = str(petition['_id'])
                if 'user_id' in petition:
                    petition['user_id'] = str(petition['user_id'])
            
            return petitions
        except Exception as e:
            print(f'Error in find_all: {str(e)}')
            return []
    
    @staticmethod
    def find_by_department(department):
        try:
            petitions = list(db.petitions.find({'department': department}).sort('created_at', -1))
            
            # Convert ObjectId to string for JSON serialization
            for petition in petitions:
                if '_id' in petition:
                    petition['_id'] = str(petition['_id'])
                if 'user_id' in petition:
                    petition['user_id'] = str(petition['user_id'])
            
            return petitions
        except Exception as e:
            print(f'Error in find_by_department: {str(e)}')
            return []
    
    @staticmethod
    def update_status(ticket_id, status):
        return db.petitions.update_one(
            {'ticket_id': ticket_id},
            {'$set': {'status': status, 'updated_at': datetime.now(UTC)}}
        )