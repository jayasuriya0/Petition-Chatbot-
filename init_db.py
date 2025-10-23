from pymongo import MongoClient
import bcrypt
from datetime import datetime, UTC

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.petition_system

# Create collections
db.create_collection('users')
db.create_collection('petitions') 
db.create_collection('departments')
db.create_collection('admins')

# Create indexes
db.users.create_index('email', unique=True)
db.departments.create_index('email', unique=True)
db.admins.create_index('email', unique=True)
db.petitions.create_index('ticket_id', unique=True)

# Create sample admin user
admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
db.admins.insert_one({
    'username': 'admin',
    'email': 'admin@petition.system',
    'password': admin_password,
    'created_at': datetime.utcnow()
})

# Create sample department
dept_password = bcrypt.hashpw('dept123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
db.departments.insert_one({
    'name': 'Public Works Department',
    'email': 'publicworks@city.gov',
    'password': dept_password,
    'categories': ['infrastructure', 'sanitation', 'public-safety'],
    'created_at': datetime.utcnow()
})

print("Database initialized successfully!")