from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from models import User, Petition, Department, Admin
from config import Config
from pymongo import MongoClient
import google.generativeai as genai
import os
from datetime import datetime, UTC, timedelta
import json
from bson import ObjectId
from email_utils import (
    generate_otp, 
    send_otp_email, 
    send_welcome_email, 
    get_otp_email_template, 
    get_welcome_email_template,
    send_petition_submission_email,
    send_petition_status_update_email,
    send_email
)
from email_templates import (
    get_high_urgency_alert_template,
    get_daily_summary_template,
    get_weekly_report_template,
    get_deadline_reminder_template
)

client = MongoClient(Config.MONGO_URI)
db = client.petition_system

# Notifications storage (in-memory for now, could be MongoDB collection)
notifications_store = []

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
CORS(app, supports_credentials=True)

# Configure Gemini AI
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-pro')

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

# AI Assistant Functions
def improve_petition_text(text, title, category):
    prompt = f"""
    Improve this petition text to make it more persuasive and professional. 
    The petition is about {category} with title: "{title}".
    
    Original text: {text}
    
    Please provide an improved version that:
    1. Is clear and concise
    2. Uses persuasive language
    3. Highlights the importance of the issue
    4. Maintains a respectful tone
    5. Includes a clear call to action
    
    Return only the improved text without any additional commentary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating improvement: {str(e)}"

def suggest_titles(description, category):
    prompt = f"""
    Based on this petition description about {category}, suggest 5 compelling titles:
    
    Description: {description}
    
    Please provide 5 title suggestions in this format:
    1. First title suggestion
    2. Second title suggestion
    3. Third title suggestion
    4. Fourth title suggestion
    5. Fifth title suggestion
    
    Make the titles concise, attention-grabbing, and relevant to the issue.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating titles: {str(e)}"

def check_clarity(text):
    prompt = f"""
    Analyze this petition text for clarity and effectiveness:
    
    Text: {text}
    
    Provide a constructive analysis with:
    1. Strengths of the current text
    2. Areas for improvement
    3. Specific suggestions to enhance clarity
    4. Missing information that would strengthen the petition
    
    Keep the feedback actionable and positive.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing clarity: {str(e)}"

def add_details(text, category, location):
    prompt = f"""
    Suggest additional details to strengthen this petition about {category} at location: {location}.
    
    Current text: {text}
    
    Suggest specific details that could be added to make the petition more compelling:
    - Quantitative data that would help
    - Specific impacts on the community
    - Timeline or urgency factors
    - Supporting evidence types
    - Personal experiences that would add weight
    
    Provide the suggestions in a bullet-point format.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating detail suggestions: {str(e)}"

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index_html():
    return render_template('index.html')

# User Routes
@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/submit-petition.html')
def submit_petition():
    return render_template('submit-petition.html')

@app.route('/track-petition.html')
def track_petition():
    return render_template('track-petition.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

# Auth Routes
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/register.html')
def register():
    return render_template('register.html')

# Admin Routes
@app.route('/admin-dashboard.html')
def admin_dashboard():
    return render_template('admin-dashboard.html')

@app.route('/verify-otp.html')
def verify_otp_page():
    return render_template('verify-otp.html')

# Department Routes  
@app.route('/department-dashboard.html')
def department_dashboard():
    return render_template('department-dashboard.html')

@app.route('/test-notifications.html')
def test_notifications():
    return render_template('test-notifications.html')

@app.route('/loading-widget-demo.html')
def loading_widget_demo():
    return render_template('loading-widget-demo.html')

@app.route('/assigned-petitions.html')
def assigned_petitions():
    return render_template('assigned-petitions.html')

@app.route('/department-analytics.html')
def department_analytics():
    return render_template('department-analytics.html')

@app.route('/department-settings.html')
def department_settings():
    return render_template('department-settings.html')

# Debug Route
@app.route('/api/debug/session')
def debug_session():
    return jsonify({
        'session': dict(session),
        'user_id': session.get('user_id'),
        'user_type': session.get('user_type')
    })

# User Routes
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        print(f"📝 Registration attempt for email: {data.get('email')}")
        
        if User.find_by_email(data['email']):
            return jsonify({'error': 'User already exists'}), 400
        
        # Generate 6-digit OTP
        otp = generate_otp()
        print(f"🔐 Generated OTP: {otp} for {data['email']}")
        
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            password=data['password']
        )
        
        # Set OTP and timestamp
        user.otp = otp
        user.otp_created_at = datetime.now(UTC)
        
        result = user.save()
        print(f"✅ User saved successfully with ID: {result.inserted_id}")
        
        # Send OTP email
        if send_otp_email(user.email, otp, user.name):
            print(f"📧 OTP email sent to {user.email}")
        else:
            print(f"⚠️ Failed to send OTP email to {user.email}")
        
        # Return immediately
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please check your email for OTP verification.',
            'email': user.email
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        user = User.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('email_verified'):
            return jsonify({'error': 'Email already verified'}), 400
        
        # Check if OTP matches
        if user.get('otp') != otp:
            return jsonify({'error': 'Invalid OTP'}), 400
        
        # Check if OTP is expired (10 minutes)
        otp_created_at = user.get('otp_created_at')
        if otp_created_at:
            # Convert string to datetime if needed
            if isinstance(otp_created_at, str):
                otp_created_at = datetime.fromisoformat(otp_created_at)
            
            # Ensure both datetimes are timezone-aware for comparison
            if otp_created_at.tzinfo is None:
                otp_created_at = otp_created_at.replace(tzinfo=UTC)
            
            current_time = datetime.now(UTC)
            time_diff = current_time - otp_created_at
            
            if time_diff > timedelta(minutes=10):
                return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400
        
        # Update user as verified
        db.users.update_one(
            {'email': email},
            {
                '$set': {
                    'email_verified': True,
                    'otp': None,
                    'otp_created_at': None
                }
            }
        )
        
        # Send welcome email
        send_welcome_email(email, user['name'])
        
        return jsonify({'message': 'Email verified successfully! You can now login.'}), 200
    except Exception as e:
        print(f"❌ OTP verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.find_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.get('email_verified'):
            return jsonify({'error': 'Email already verified'}), 400
        
        print(f"🔄 Resending OTP to: {email}")
        
        # Generate new OTP
        otp = generate_otp()
        otp_created_at = datetime.now(UTC)
        
        # Update user with new OTP
        db.users.update_one(
            {'email': email},
            {
                '$set': {
                    'otp': otp,
                    'otp_created_at': otp_created_at
                }
            }
        )
        
        # Send OTP email
        if send_otp_email(email, otp, user['name']):
            print(f"✅ OTP resent successfully to: {email}")
            return jsonify({'message': 'OTP sent successfully!'}), 200
        else:
            print(f"❌ Failed to send OTP to: {email}")
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        user = User.find_by_email(data['email'])
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not User.check_password(user['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if email is verified
        if not user.get('email_verified', False):
            return jsonify({
                'error': 'Email not verified',
                'requires_verification': True,
                'email': user['email']
            }), 403
        
        session.clear()
        session['user_id'] = str(user['_id'])
        session['user_type'] = 'user'
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Petition Routes
@app.route('/api/petitions', methods=['POST'])
def create_petition():
    try:
        data = request.json
        petition = Petition(
            user_id=data['user_id'],
            title=data['title'],
            category=data['category'],
            department=data['department'],
            description=data['description'],
            location=data['location'],
            urgency=data['urgency'],
            full_name=data['full_name'],
            email=data['email'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            attachments=data.get('attachments', [])
        )
        result = petition.save()
        
        # Send submission confirmation email to user
        send_petition_submission_email(
            user_email=petition.email,
            user_name=petition.full_name,
            ticket_id=petition.ticket_id,
            title=petition.title
        )
        print(f"📧 Petition submission email queued for user: {petition.email}")
        
        # Add notification to store
        notification = {
            'id': str(ObjectId()),
            'ticket_id': petition.ticket_id,
            'title': petition.title,
            'department': petition.department,
            'urgency': petition.urgency,
            'type': 'new_petition',
            'timestamp': datetime.now(UTC).isoformat(),
            'read': False
        }
        notifications_store.append(notification)
        print(f"🔔 Notification added for department: {petition.department}")
        
        # If high urgency, send email alert to department
        if petition.urgency == 'high':
            # Get department email
            dept = db.departments.find_one({'name': petition.department})
            if dept and dept.get('email'):
                petition_data = {
                    'ticket_id': petition.ticket_id,
                    'title': petition.title,
                    'description': petition.description,
                    'department': petition.department,
                    'category': petition.category,
                    'name': petition.full_name,
                    'email': petition.email,
                    'created_at': datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
                }
                
                html_content = get_high_urgency_alert_template(petition_data)
                send_email(
                    to_email=dept['email'],
                    subject=f"🚨 HIGH URGENCY PETITION - {petition.ticket_id}",
                    html_body=html_content
                )
                print(f"🚨 High urgency email sent to department: {dept['email']}")
        
        return jsonify({
            'message': 'Petition submitted successfully',
            'ticket_id': petition.ticket_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/petitions/user/<user_id>')
def get_user_petitions(user_id):
    try:
        petitions = Petition.find_by_user(user_id)
        return jsonify({'petitions': petitions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/petitions/track/<ticket_id>')
def api_track_petition(ticket_id):
    try:
        print(f"🔍 Tracking petition: {ticket_id}")
        petition = Petition.find_by_ticket(ticket_id)
        if petition:
            print(f"✅ Found petition: {petition.get('title', 'N/A')}")
            return jsonify({'petition': petition}), 200
        else:
            print(f"❌ Petition not found: {ticket_id}")
            return jsonify({'error': 'Petition not found'}), 404
    except Exception as e:
        print(f"❌ Error tracking petition {ticket_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# AI Assistant Routes
@app.route('/api/ai/improve', methods=['POST'])
def ai_improve():
    try:
        data = request.json
        improved_text = improve_petition_text(
            data['text'],
            data.get('title', ''),
            data.get('category', '')
        )
        return jsonify({'improved_text': improved_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/suggest-titles', methods=['POST'])
def ai_suggest_titles():
    try:
        data = request.json
        titles = suggest_titles(
            data['description'],
            data.get('category', '')
        )
        return jsonify({'suggested_titles': titles}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/check-clarity', methods=['POST'])
def ai_check_clarity():
    try:
        data = request.json
        analysis = check_clarity(data['text'])
        return jsonify({'clarity_analysis': analysis}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/add-details', methods=['POST'])
def ai_add_details():
    try:
        data = request.json
        details = add_details(
            data['text'],
            data.get('category', ''),
            data.get('location', '')
        )
        return jsonify({'detail_suggestions': details}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Department Routes
@app.route('/api/department/login', methods=['POST'])
def department_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        otp = data.get('otp')
        
        department = Department.find_by_email(email)
        
        if not department:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # If OTP is provided, verify it
        if otp:
            if department.get('otp') != otp:
                return jsonify({'error': 'Invalid OTP'}), 400
            
            # Check if OTP is expired (10 minutes)
            otp_created_at = department.get('otp_created_at')
            if otp_created_at:
                # Convert string to datetime if needed
                if isinstance(otp_created_at, str):
                    otp_created_at = datetime.fromisoformat(otp_created_at)
                
                # Ensure both datetimes are timezone-aware for comparison
                if otp_created_at.tzinfo is None:
                    otp_created_at = otp_created_at.replace(tzinfo=UTC)
                
                current_time = datetime.now(UTC)
                time_diff = current_time - otp_created_at
                
                if time_diff > timedelta(minutes=10):
                    return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400
            
            print(f"✅ Department OTP verified for: {email}")
            
            # Clear OTP but DON'T mark as verified (require OTP every time)
            db.departments.update_one(
                {'email': email},
                {
                    '$set': {
                        'otp': None,
                        'otp_created_at': None
                    }
                }
            )
            
            # Set session
            session.clear()
            session['department_id'] = str(department['_id'])
            session['user_type'] = 'department'
            session.permanent = True
            
            return jsonify({
                'message': 'Login successful',
                'department': {
                    'id': str(department['_id']),
                    'name': department['name'],
                    'email': department['email']
                }
            }), 200
        
        # If no OTP, verify password and send OTP
        if not Department.check_password(department['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        print(f"🔐 Department password verified, sending OTP to: {email}")
        
        # Generate and send OTP
        new_otp = generate_otp()
        otp_created_at = datetime.now(UTC)
        
        db.departments.update_one(
            {'email': email},
            {
                '$set': {
                    'otp': new_otp,
                    'otp_created_at': otp_created_at
                }
            }
        )
        
        # Send OTP email
        if send_otp_email(email, new_otp, department['name']):
            print(f"✅ OTP sent to department: {email}")
            return jsonify({
                'message': 'OTP sent to your email',
                'requires_otp': True
            }), 200
        else:
            return jsonify({'error': 'Failed to send OTP'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/departments', methods=['GET'])
def get_departments():
    try:
        departments = Department.find_all()
        dept_list = []
        for dept in departments:
            dept_list.append({
                'id': str(dept['_id']),
                'name': dept['name'],
                'email': dept['email'],
                'categories': dept.get('categories', [])
            })
        return jsonify({'departments': dept_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments', methods=['POST'])
def create_department():
    try:
        # Check if admin is logged in
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        
        # Check if department already exists
        if Department.find_by_email(data['email']):
            return jsonify({'error': 'Department with this email already exists'}), 400
        
        department = Department(
            name=data['dept_name'],
            email=data['email'],
            password=data['password'],
            categories=data.get('categories', []),
            profile=data.get('profile'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        
        result = department.save()
        
        print(f"✅ Department created: {data['dept_name']}")
        
        return jsonify({
            'message': 'Department created successfully',
            'department_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"❌ Error creating department: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments/<dept_id>', methods=['GET'])
def get_department(dept_id):
    try:
        # Check if admin is logged in
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Get petition statistics for this department
        total_petitions = db.petitions.count_documents({'department': department['name']})
        pending_petitions = db.petitions.count_documents({'department': department['name'], 'status': 'pending'})
        resolved_petitions = db.petitions.count_documents({'department': department['name'], 'status': 'resolved'})
        
        dept_data = {
            'id': str(department['_id']),
            'name': department['name'],
            'email': department['email'],
            'categories': department.get('categories', []),
            'profile': department.get('profile'),
            'phone': department.get('phone'),
            'address': department.get('address'),
            'created_at': department.get('created_at'),
            'total_petitions': total_petitions,
            'pending_petitions': pending_petitions,
            'resolved_petitions': resolved_petitions
        }
        
        return jsonify({'department': dept_data}), 200
        
    except Exception as e:
        print(f"❌ Error fetching department: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments/<dept_id>', methods=['PUT'])
def update_department(dept_id):
    try:
        # Check if admin is logged in
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        
        update_data = {
            'name': data['name'],
            'email': data['email'],
            'categories': data.get('categories', []),
            'profile': data.get('profile'),
            'phone': data.get('phone'),
            'address': data.get('address')
        }
        
        result = db.departments.update_one(
            {'_id': ObjectId(dept_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ Department updated: {data['name']}")
            return jsonify({'message': 'Department updated successfully'}), 200
        else:
            return jsonify({'error': 'Department not found or no changes made'}), 404
            
    except Exception as e:
        print(f"❌ Error updating department: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments/<dept_id>', methods=['DELETE'])
def delete_department(dept_id):
    try:
        # Check if admin is logged in
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        result = db.departments.delete_one({'_id': ObjectId(dept_id)})
        
        if result.deleted_count > 0:
            print(f"✅ Department deleted: {dept_id}")
            return jsonify({'message': 'Department deleted successfully'}), 200
        else:
            return jsonify({'error': 'Department not found'}), 404
            
    except Exception as e:
        print(f"❌ Error deleting department: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/department/petitions/<department_name>')
def get_department_petitions(department_name):
    try:
        print(f"🔍 Fetching petitions for department: {department_name}")
        
        # Check if department is authenticated
        if 'department_id' not in session:
            print(f"❌ No department session found")
            return jsonify({'error': 'Not authenticated'}), 401
        
        petitions = Petition.find_by_department(department_name)
        
        # Convert ObjectId to string for JSON serialization
        for petition in petitions:
            if '_id' in petition:
                petition['_id'] = str(petition['_id'])
        
        print(f"✅ Found {len(petitions)} petitions for {department_name}")
        return jsonify({'petitions': petitions}), 200
        
    except Exception as e:
        print(f"❌ Error fetching department petitions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/department/current')
def get_current_department():
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        department = db.departments.find_one({'_id': ObjectId(session['department_id'])})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Get petition statistics
        total_petitions = db.petitions.count_documents({'department': department['name']})
        pending_petitions = db.petitions.count_documents({'department': department['name'], 'status': 'pending'})
        in_progress_petitions = db.petitions.count_documents({'department': department['name'], 'status': 'in_progress'})
        resolved_petitions = db.petitions.count_documents({'department': department['name'], 'status': 'resolved'})
        
        dept_data = {
            'id': str(department['_id']),
            'name': department['name'],
            'email': department['email'],
            'categories': department.get('categories', []),
            'profile': department.get('profile'),
            'phone': department.get('phone'),
            'address': department.get('address'),
            'statistics': {
                'total': total_petitions,
                'pending': pending_petitions,
                'in_progress': in_progress_petitions,
                'resolved': resolved_petitions
            }
        }
        
        return jsonify({'department': dept_data}), 200
        
    except Exception as e:
        print(f"❌ Error fetching department: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Assigned Petitions API - Advanced filtering
@app.route('/api/department/assigned-petitions')
def get_assigned_petitions():
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        department = db.departments.find_one({'_id': ObjectId(session['department_id'])})
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Get filter parameters
        status_filter = request.args.get('status', '')
        urgency_filter = request.args.get('urgency', '')
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        
        # Build query
        query = {'department': department['name']}
        
        if status_filter:
            query['status'] = status_filter
        if urgency_filter:
            query['urgency'] = urgency_filter
        if category_filter:
            query['category'] = category_filter
        if search_query:
            query['$or'] = [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}},
                {'ticket_id': {'$regex': search_query, '$options': 'i'}}
            ]
        
        petitions = list(db.petitions.find(query).sort('created_at', -1))
        
        # Convert ObjectId to string
        for petition in petitions:
            if '_id' in petition:
                petition['_id'] = str(petition['_id'])
            # Format date
            if 'created_at' in petition:
                petition['created_at'] = petition['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'petitions': petitions}), 200
        
    except Exception as e:
        print(f"❌ Error fetching assigned petitions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Department Analytics API
@app.route('/api/department/analytics')
def get_department_analytics():
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        department = db.departments.find_one({'_id': ObjectId(session['department_id'])})
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Get time range
        days = int(request.args.get('days', 30))
        from datetime import datetime, timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        dept_name = department['name']
        
        # Total petitions in time range
        total_petitions = db.petitions.count_documents({
            'department': dept_name,
            'created_at': {'$gte': start_date}
        })
        
        # Previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_petitions = db.petitions.count_documents({
            'department': dept_name,
            'created_at': {'$gte': prev_start, '$lt': start_date}
        })
        
        # Calculate trend
        petition_trend = 0
        if prev_petitions > 0:
            petition_trend = round(((total_petitions - prev_petitions) / prev_petitions) * 100, 1)
        
        # Resolved petitions
        resolved_petitions = db.petitions.count_documents({
            'department': dept_name,
            'status': 'resolved',
            'created_at': {'$gte': start_date}
        })
        
        # Resolution rate
        resolution_rate = 0
        if total_petitions > 0:
            resolution_rate = round((resolved_petitions / total_petitions) * 100, 1)
        
        # Previous resolution rate
        prev_resolved = db.petitions.count_documents({
            'department': dept_name,
            'status': 'resolved',
            'created_at': {'$gte': prev_start, '$lt': start_date}
        })
        prev_resolution_rate = 0
        if prev_petitions > 0:
            prev_resolution_rate = round((prev_resolved / prev_petitions) * 100, 1)
        
        resolution_trend = round(resolution_rate - prev_resolution_rate, 1)
        
        # Status distribution
        status_counts = {
            'pending': db.petitions.count_documents({'department': dept_name, 'status': 'pending'}),
            'in_progress': db.petitions.count_documents({'department': dept_name, 'status': 'in_progress'}),
            'resolved': db.petitions.count_documents({'department': dept_name, 'status': 'resolved'}),
            'rejected': db.petitions.count_documents({'department': dept_name, 'status': 'rejected'})
        }
        
        # Category distribution
        pipeline = [
            {'$match': {'department': dept_name}},
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]
        categories = list(db.petitions.aggregate(pipeline))
        
        # Trend data (last 6 months)
        trend_data = []
        for i in range(5, -1, -1):
            month_start = datetime.now() - timedelta(days=i*30)
            month_end = datetime.now() - timedelta(days=(i-1)*30) if i > 0 else datetime.now()
            
            submitted = db.petitions.count_documents({
                'department': dept_name,
                'created_at': {'$gte': month_start, '$lt': month_end}
            })
            
            resolved = db.petitions.count_documents({
                'department': dept_name,
                'status': 'resolved',
                'created_at': {'$gte': month_start, '$lt': month_end}
            })
            
            trend_data.append({
                'month': month_start.strftime('%b'),
                'submitted': submitted,
                'resolved': resolved
            })
        
        # Urgency distribution
        high_urgency = db.petitions.count_documents({'department': dept_name, 'urgency': 'high'})
        
        analytics = {
            'metrics': {
                'total_petitions': total_petitions,
                'petition_trend': petition_trend,
                'resolution_rate': resolution_rate,
                'resolution_trend': resolution_trend,
                'avg_response_time': 2.3,  # Can be calculated from actual data
                'response_trend': -0.5,
                'satisfaction_score': 4.2,  # Can be from user ratings
                'satisfaction_trend': 0.3
            },
            'status_distribution': status_counts,
            'category_distribution': [{'name': cat['_id'], 'count': cat['count']} for cat in categories],
            'trend_data': trend_data,
            'performance': {
                'first_response': '1.8h',
                'sla_compliance': 95,
                'escalated_cases': high_urgency,
                'reopened_petitions': db.petitions.count_documents({
                    'department': dept_name,
                    'status': 'in_progress',
                    'updated_at': {'$exists': True}
                })
            }
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        print(f"❌ Error fetching analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Department Settings API - Get settings
@app.route('/api/department/settings', methods=['GET'])
def get_department_settings():
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        department = db.departments.find_one({'_id': ObjectId(session['department_id'])})
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        settings = {
            'department': {
                'name': department.get('name', ''),
                'email': department.get('email', ''),
                'phone': department.get('phone', ''),
                'location': department.get('address', ''),
                'description': department.get('description', '')
            },
            'notifications': department.get('notifications', {
                'new_petition_alerts': True,
                'priority_alerts': True,
                'daily_summary': False,
                'weekly_report': True
            }),
            'auto_assignment': department.get('auto_assignment', {
                'enabled': True,
                'priority_threshold': 'high',
                'max_workload': 10
            }),
            'sla': department.get('sla', {
                'first_response': 2,
                'resolution_time': 5,
                'escalation_time': 3,
                'reminder_frequency': 'daily'
            })
        }
        
        return jsonify(settings), 200
        
    except Exception as e:
        print(f"❌ Error fetching settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Department Settings API - Update settings
@app.route('/api/department/settings', methods=['PUT'])
def update_department_settings():
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.json
        
        update_data = {}
        if 'department' in data:
            for key, value in data['department'].items():
                if key == 'name':
                    update_data['name'] = value
                elif key == 'email':
                    update_data['email'] = value
                elif key == 'phone':
                    update_data['phone'] = value
                elif key == 'location':
                    update_data['address'] = value
                elif key == 'description':
                    update_data['description'] = value
        
        if 'notifications' in data:
            update_data['notifications'] = data['notifications']
        
        if 'auto_assignment' in data:
            update_data['auto_assignment'] = data['auto_assignment']
        
        if 'sla' in data:
            update_data['sla'] = data['sla']
        
        result = db.departments.update_one(
            {'_id': ObjectId(session['department_id'])},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Settings updated successfully'}), 200
        else:
            return jsonify({'message': 'No changes made'}), 200
        
    except Exception as e:
        print(f"❌ Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/petitions/<ticket_id>/status', methods=['PUT'])
def update_petition_status(ticket_id):
    try:
        data = request.json
        new_status = data['status']
        rejection_reason = data.get('rejection_reason', None)
        
        # Get current petition to compare status and get user info
        current_petition = Petition.find_by_ticket(ticket_id)
        if not current_petition:
            return jsonify({'error': 'Petition not found'}), 404
        
        old_status = current_petition.get('status')
        
        # Validate rejection reason if status is rejected
        if new_status == 'rejected' and not rejection_reason:
            return jsonify({'error': 'Rejection reason is required when rejecting a petition'}), 400
        
        # Update the status and rejection reason
        update_data = {'status': new_status}
        if rejection_reason:
            update_data['rejection_reason'] = rejection_reason
        
        result = db.petitions.update_one(
            {'ticket_id': ticket_id},
            {
                '$set': update_data,
                '$currentDate': {'updated_at': True}
            }
        )
        
        if result.modified_count > 0:
            # Send email notification if status changed
            if old_status != new_status:
                try:
                    # Send rejection email if status is rejected
                    if new_status == 'rejected' and rejection_reason:
                        from email_templates import get_rejection_email_template
                        email_body = get_rejection_email_template(current_petition, rejection_reason)
                        send_email(
                            to_email=current_petition['email'],
                            subject=f"Petition Rejected - {current_petition['ticket_id']}",
                            html_body=email_body
                        )
                        print(f"📧 Rejection email queued for: {current_petition['email']} (ticket: {ticket_id})")
                    else:
                        # Send regular status update email
                        send_petition_status_update_email(
                            user_email=current_petition['email'],
                            user_name=current_petition['full_name'],
                            ticket_id=ticket_id,
                            title=current_petition['title'],
                            old_status=old_status,
                            new_status=new_status
                        )
                        print(f"📧 Status update email queued for: {current_petition['email']} (ticket: {ticket_id})")
                    print(f"   Status changed: {old_status} → {new_status}")
                except Exception as email_error:
                    print(f"⚠️ Email error for {ticket_id}: {str(email_error)}")
                    # Don't fail the request if email fails
                    pass
            
            return jsonify({
                'message': 'Status updated successfully',
                'old_status': old_status,
                'new_status': new_status
            }), 200
        else:
            return jsonify({'error': 'No changes made'}), 400
            
    except Exception as e:
        print(f"❌ Error updating petition status: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Admin Routes
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        admin = Admin.find_by_email(data['email'])
        
        if admin and Admin.check_password(admin['password'], data['password']):
            session['admin_id'] = str(admin['_id'])
            session['user_type'] = 'admin'
            return jsonify({
                'message': 'Login successful',
                'admin': {
                    'id': str(admin['_id']),
                    'username': admin['username'],
                    'email': admin['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/petitions')
def get_all_petitions():
    try:
        print("🔍 Admin fetching all petitions...")
        
        # Check if admin is authenticated
        if 'admin_id' not in session:
            print("❌ Admin not authenticated")
            return jsonify({'error': 'Not authenticated'}), 401
        
        petitions = Petition.find_all()
        print(f"✅ Found {len(petitions)} petitions")
        
        return jsonify({'petitions': petitions}), 200
        
    except Exception as e:
        print(f"❌ Error fetching all petitions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats')
def get_admin_stats():
    try:
        print("Fetching admin stats...")
        
        # Fetch all data
        petitions = Petition.find_all()
        departments = Department.find_all()
        users = list(db.users.find())
        
        print(f"Found {len(petitions)} petitions, {len(departments)} departments, {len(users)} users")
        
        # Basic stats
        total = len(petitions)
        pending = len([p for p in petitions if p.get('status') == 'pending'])
        in_progress = len([p for p in petitions if p.get('status') == 'in_progress'])
        resolved = len([p for p in petitions if p.get('status') == 'resolved'])
        
        print(f"Stats: total={total}, pending={pending}, in_progress={in_progress}, resolved={resolved}")
        
        # Department-wise stats
        dept_stats = {}
        for dept in departments:
            dept_name = dept['name']
            dept_petitions = [p for p in petitions if p.get('department') == dept_name]
            dept_stats[dept_name] = {
                'total': len(dept_petitions),
                'pending': len([p for p in dept_petitions if p.get('status') == 'pending']),
                'resolved': len([p for p in dept_petitions if p.get('status') == 'resolved'])
            }
        
        # Helper function to get timezone-aware datetime
        def get_aware_datetime(dt):
            if dt is None:
                return datetime.min.replace(tzinfo=UTC)
            if isinstance(dt, str):
                # Try to parse ISO format string
                try:
                    parsed = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                    if parsed.tzinfo is None:
                        return parsed.replace(tzinfo=UTC)
                    return parsed
                except:
                    return datetime.min.replace(tzinfo=UTC)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt
        
        # Recent petitions (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        recent_petitions = []
        for p in petitions:
            created_at = get_aware_datetime(p.get('created_at'))
            if created_at >= thirty_days_ago:
                recent_petitions.append(p)
        
        # Daily stats for last 7 days
        daily_stats = []
        for i in range(6, -1, -1):
            day = datetime.now(UTC) - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_petitions = []
            for p in petitions:
                created_at = get_aware_datetime(p.get('created_at'))
                if day_start <= created_at < day_end:
                    day_petitions.append(p)
            
            daily_stats.append({
                'date': day.strftime('%Y-%m-%d'),
                'total': len(day_petitions),
                'pending': len([p for p in day_petitions if p.get('status') == 'pending']),
                'resolved': len([p for p in day_petitions if p.get('status') == 'resolved'])
            })
        
        stats_response = {
            'total_petitions': total,
            'pending': pending,
            'in_progress': in_progress,
            'resolved': resolved,
            'total_users': len(users),
            'total_departments': len(departments),
            'department_stats': dept_stats,
            'daily_stats': daily_stats,
            'recent_petitions_count': len(recent_petitions)
        }
        
        print(f"Returning stats: {stats_response}")
        return jsonify(stats_response), 200
        
    except Exception as e:
        print(f"Error in get_admin_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'total_petitions': 0,
            'pending': 0,
            'in_progress': 0,
            'resolved': 0,
            'total_users': 0,
            'total_departments': 0
        }), 500

# Dashboard Routes
@app.route('/api/dashboard/stats/<user_id>')
def get_dashboard_stats(user_id):
    try:
        petitions = Petition.find_by_user(user_id)
        total = len(petitions)
        pending = len([p for p in petitions if p['status'] == 'pending'])
        in_progress = len([p for p in petitions if p['status'] == 'in_progress'])
        resolved = len([p for p in petitions if p['status'] == 'resolved'])
        
        # Recent petitions (last 5)
        recent_petitions = petitions[:5]
        
        return jsonify({
            'total_petitions': total,
            'pending': pending,
            'in_progress': in_progress,
            'resolved': resolved,
            'recent_petitions': recent_petitions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Deadline Management Routes
@app.route('/api/petitions/<ticket_id>/deadline', methods=['GET'])
def get_petition_deadline(ticket_id):
    """Get deadline information for a specific petition"""
    try:
        petition = Petition.find_by_ticket(ticket_id)
        if not petition:
            return jsonify({'error': 'Petition not found'}), 404
        
        deadline = petition.get('deadline')
        if deadline:
            # Convert to aware datetime if needed
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            elif deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=UTC)
            
            now = datetime.now(UTC)
            time_remaining = deadline - now
            hours_remaining = time_remaining.total_seconds() / 3600
            is_overdue = time_remaining.total_seconds() < 0
            
            return jsonify({
                'deadline': deadline.isoformat(),
                'hours_remaining': hours_remaining,
                'is_overdue': is_overdue,
                'status': petition.get('status')
            }), 200
        else:
            return jsonify({'error': 'No deadline set'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/petitions/<ticket_id>/extend-deadline', methods=['POST'])
def extend_petition_deadline(ticket_id):
    """Extend the deadline for a petition"""
    try:
        data = request.json
        hours_to_extend = data.get('hours', 24)
        
        petition = Petition.find_by_ticket(ticket_id)
        if not petition:
            return jsonify({'error': 'Petition not found'}), 404
        
        current_deadline = petition.get('deadline')
        if isinstance(current_deadline, str):
            current_deadline = datetime.fromisoformat(current_deadline.replace('Z', '+00:00'))
        elif current_deadline.tzinfo is None:
            current_deadline = current_deadline.replace(tzinfo=UTC)
        
        from datetime import timedelta
        new_deadline = current_deadline + timedelta(hours=hours_to_extend)
        
        db.petitions.update_one(
            {'ticket_id': ticket_id},
            {'$set': {'deadline': new_deadline, 'updated_at': datetime.now(UTC)}}
        )
        
        return jsonify({
            'message': 'Deadline extended successfully',
            'new_deadline': new_deadline.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/overdue-petitions')
def get_overdue_petitions():
    """Get all overdue petitions"""
    try:
        petitions = Petition.find_all()
        now = datetime.now(UTC)
        overdue = []
        
        for petition in petitions:
            if petition.get('status') in ['pending', 'in_progress']:
                deadline = petition.get('deadline')
                if deadline:
                    if isinstance(deadline, str):
                        deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    elif deadline.tzinfo is None:
                        deadline = deadline.replace(tzinfo=UTC)
                    
                    if deadline < now:
                        time_overdue = now - deadline
                        petition['hours_overdue'] = time_overdue.total_seconds() / 3600
                        overdue.append(petition)
        
        return jsonify({
            'overdue_petitions': overdue,
            'count': len(overdue)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/send-deadline-reminders', methods=['POST'])
def send_deadline_reminders():
    """Send deadline reminder emails to departments for petitions approaching deadline"""
    try:
        petitions = Petition.find_all()
        now = datetime.now(UTC)
        reminders_sent = 0
        
        for petition in petitions:
            if petition.get('status') in ['pending', 'in_progress']:
                deadline = petition.get('deadline')
                if deadline:
                    if isinstance(deadline, str):
                        deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    elif deadline.tzinfo is None:
                        deadline = deadline.replace(tzinfo=UTC)
                    
                    time_remaining = deadline - now
                    hours_remaining = time_remaining.total_seconds() / 3600
                    
                    # Send reminders for petitions with less than 48 hours remaining
                    if 0 < hours_remaining < 48:
                        # Get department email
                        dept_name = petition.get('department')
                        department = Department.find_by_email(dept_name.lower().replace(' ', '_') + '@dept.com')
                        
                        if department and department.get('email'):
                            email_html = get_deadline_reminder_template(petition, hours_remaining)
                            subject = f"⚠️ Deadline Reminder: Petition {petition.get('ticket_id')}"
                            
                            try:
                                send_email(department['email'], subject, email_html)
                                reminders_sent += 1
                                print(f"Sent deadline reminder to {department['email']} for {petition.get('ticket_id')}")
                            except Exception as email_error:
                                print(f"Failed to send reminder email: {str(email_error)}")
        
        return jsonify({
            'message': f'Sent {reminders_sent} deadline reminder(s)',
            'reminders_sent': reminders_sent
        }), 200
        
    except Exception as e:
        print(f"Error sending deadline reminders: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Profile Routes
@app.route('/api/profile/<user_id>')
def get_user_profile(user_id):
    try:
        user = User.find_by_id(ObjectId(user_id))
        if user:
            return jsonify({
                'name': user['name'],
                'email': user['email'],
                'phone': user.get('phone', ''),
                'address': user.get('address', ''),
                'joined_date': user['created_at']
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    try:
        data = request.json
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'name': data['name'],
                'phone': data.get('phone', ''),
                'address': data.get('address', ''),
                'updated_at': datetime.now(UTC)
            }}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'Profile not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Petition Tracking Routes
@app.route('/api/petitions/search', methods=['POST'])
def search_petitions():
    try:
        data = request.json
        print(f'Search request data: {data}')
        
        query = {}
        
        # Handle user_id query first
        if data.get('user_id'):
            query['user_id'] = str(data['user_id'])
            print(f'Using user_id: {query["user_id"]}')
        
        if data.get('ticket_id'):
            query['ticket_id'] = data['ticket_id']
        if data.get('status'):
            query['status'] = data['status']
        if data.get('category'):
            query['category'] = data['category']
        if data.get('date_from'):
            query['created_at'] = {'$gte': datetime.fromisoformat(data['date_from'])}
        if data.get('date_to'):
            if 'created_at' in query:
                query['created_at']['$lte'] = datetime.fromisoformat(data['date_to'])
            else:
                query['created_at'] = {'$lte': datetime.fromisoformat(data['date_to'])}
        
        print(f'Final MongoDB query: {query}')
        
        cursor = db.petitions.find(query).sort('created_at', -1)
        petitions = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for petition in petitions:
            petition['_id'] = str(petition['_id'])
        
        print(f'Found {len(petitions)} petitions')
        return jsonify({'petitions': petitions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

@app.route('/api/check-auth')
def check_auth():
    if 'user_id' in session or 'department_id' in session or 'admin_id' in session:
        user_type = session.get('user_type', 'user')
        return jsonify({'authenticated': True, 'user_type': user_type}), 200
    return jsonify({'authenticated': False}), 401

# Current User ID Route
@app.route('/api/current-user')
def get_current_user():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.find_by_id(ObjectId(user_id))
        if user:
            return jsonify({
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email']
            }), 200
    elif 'department_id' in session:
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        if department:
            return jsonify({
                'id': str(department['_id']),
                'name': department['name'],
                'email': department['email'],
                'type': 'department'
            }), 200
    elif 'admin_id' in session:
        admin_id = session['admin_id']
        admin = db.admins.find_one({'_id': ObjectId(admin_id)})
        if admin:
            return jsonify({
                'id': str(admin['_id']),
                'name': admin['username'],
                'email': admin['email'],
                'type': 'admin'
            }), 200
    
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/profile/current_user_id')
def get_current_user_id():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({'user_id': user_id}), 200
    else:
        return jsonify({'error': 'Not logged in'}), 401

# ============= NOTIFICATION SYSTEM APIs =============

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for the logged-in department"""
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authorized'}), 401
        
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        dept_name = department['name']
        
        # Filter notifications for this department
        dept_notifications = [
            notif for notif in notifications_store 
            if notif['department'] == dept_name
        ]
        
        # Sort by timestamp (newest first)
        dept_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        print(f"📬 Fetched {len(dept_notifications)} notifications for {dept_name}")
        
        return jsonify({
            'success': True,
            'notifications': dept_notifications,
            'count': len(dept_notifications),
            'unread_count': sum(1 for n in dept_notifications if not n['read'])
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching notifications: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authorized'}), 401
        
        # Find notification by ID
        notification = next((n for n in notifications_store if n['id'] == notification_id), None)
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Verify department ownership
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if notification['department'] != department['name']:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Mark as read
        notification['read'] = True
        
        print(f"✅ Notification {notification_id} marked as read")
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        }), 200
        
    except Exception as e:
        print(f"❌ Error marking notification as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/count', methods=['GET'])
def get_unread_notification_count():
    """Get count of unread notifications for the logged-in department"""
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authorized'}), 401
        
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        dept_name = department['name']
        
        # Count unread notifications for this department
        unread_count = sum(
            1 for notif in notifications_store 
            if notif['department'] == dept_name and not notif['read']
        )
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting notification count: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/mark-all-read', methods=['PUT'])
def mark_all_notifications_read():
    """Mark all notifications as read for the logged-in department"""
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authorized'}), 401
        
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        dept_name = department['name']
        
        # Mark all notifications for this department as read
        marked_count = 0
        for notif in notifications_store:
            if notif['department'] == dept_name and not notif['read']:
                notif['read'] = True
                marked_count += 1
        
        print(f"✅ Marked {marked_count} notifications as read for {dept_name}")
        
        return jsonify({
            'success': True,
            'message': f'Marked {marked_count} notifications as read'
        }), 200
        
    except Exception as e:
        print(f"❌ Error marking all notifications as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============= REPORT GENERATION Functions =============

def send_daily_report(department_name, dept_email):
    """Generate and send daily summary report for a department"""
    try:
        # Get date range (last 24 hours)
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)
        
        # Query petitions for this department in last 24 hours
        petitions_today = list(db.petitions.find({
            'department': department_name,
            'created_at': {'$gte': yesterday}
        }))
        
        # Calculate statistics
        new_petitions = len(petitions_today)
        
        resolved_today = db.petitions.count_documents({
            'department': department_name,
            'status': 'resolved',
            'updated_at': {'$gte': yesterday}
        })
        
        pending = db.petitions.count_documents({
            'department': department_name,
            'status': 'pending'
        })
        
        high_urgency = db.petitions.count_documents({
            'department': department_name,
            'urgency': 'high',
            'status': {'$ne': 'resolved'}
        })
        
        # Get high urgency petitions list (top 5)
        high_urgency_petitions = list(db.petitions.find({
            'department': department_name,
            'urgency': 'high',
            'status': {'$ne': 'resolved'}
        }).sort('created_at', -1).limit(5))
        
        # Get new petitions today (top 5)
        new_today = petitions_today[:5] if len(petitions_today) > 5 else petitions_today
        
        # Prepare data for template
        summary_data = {
            'department_name': department_name,
            'date': now.strftime('%B %d, %Y'),
            'new_petitions': new_petitions,
            'resolved_today': resolved_today,
            'pending': pending,
            'high_urgency': high_urgency,
            'high_urgency_petitions': [
                {
                    'ticket_id': p['ticket_id'],
                    'title': p['title'],
                    'urgency': p['urgency'],
                    'category': p['category']
                }
                for p in high_urgency_petitions
            ],
            'new_today': [
                {
                    'ticket_id': p['ticket_id'],
                    'title': p['title'],
                    'urgency': p['urgency'],
                    'category': p['category']
                }
                for p in new_today
            ]
        }
        
        # Generate HTML template
        html_content = get_daily_summary_template(summary_data)
        
        # Send email
        send_email(
            to_email=dept_email,
            subject=f"📊 Daily Summary Report - {department_name} - {now.strftime('%B %d, %Y')}",
            html_body=html_content
        )
        
        print(f"📧 Daily report sent to {department_name} ({dept_email})")
        return True
        
    except Exception as e:
        print(f"❌ Error sending daily report to {department_name}: {str(e)}")
        return False

def send_weekly_report(department_name, dept_email):
    """Generate and send weekly performance report for a department"""
    try:
        # Get date ranges
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        # Query petitions for this week
        petitions_this_week = list(db.petitions.find({
            'department': department_name,
            'created_at': {'$gte': week_ago}
        }))
        
        # Query petitions for previous week (for trends)
        petitions_last_week = list(db.petitions.find({
            'department': department_name,
            'created_at': {'$gte': two_weeks_ago, '$lt': week_ago}
        }))
        
        # Calculate statistics
        total_petitions = len(petitions_this_week)
        prev_total = len(petitions_last_week)
        
        resolved_count = sum(1 for p in petitions_this_week if p['status'] == 'resolved')
        resolution_rate = (resolved_count / total_petitions * 100) if total_petitions > 0 else 0
        
        prev_resolved = sum(1 for p in petitions_last_week if p['status'] == 'resolved')
        prev_resolution_rate = (prev_resolved / prev_total * 100) if prev_total > 0 else 0
        
        # Status breakdown
        status_breakdown = {
            'resolved': sum(1 for p in petitions_this_week if p['status'] == 'resolved'),
            'in_progress': sum(1 for p in petitions_this_week if p['status'] == 'in-progress'),
            'pending': sum(1 for p in petitions_this_week if p['status'] == 'pending')
        }
        
        # Calculate average response time (mock - could be calculated from actual timestamps)
        avg_response_time = "2.5 hours"
        response_trend = 15  # Mock improvement percentage
        
        # Satisfaction score (mock - could come from user feedback)
        satisfaction_score = 4.5
        satisfaction_trend = 5
        
        # Generate insights
        insights = []
        
        if total_petitions > prev_total:
            increase_pct = ((total_petitions - prev_total) / prev_total * 100) if prev_total > 0 else 100
            insights.append(f"Petition volume increased by {increase_pct:.1f}% compared to last week")
        elif total_petitions < prev_total:
            decrease_pct = ((prev_total - total_petitions) / prev_total * 100) if prev_total > 0 else 0
            insights.append(f"Petition volume decreased by {decrease_pct:.1f}% compared to last week")
        
        if resolution_rate > prev_resolution_rate:
            insights.append(f"Resolution rate improved by {(resolution_rate - prev_resolution_rate):.1f}%")
        
        if status_breakdown['pending'] > total_petitions * 0.3:
            insights.append(f"High number of pending petitions ({status_breakdown['pending']}) - consider prioritizing")
        
        if not insights:
            insights.append("Performance is stable compared to last week")
        
        # Prepare data for template
        report_data = {
            'department_name': department_name,
            'week_start': week_ago.strftime('%B %d'),
            'week_end': now.strftime('%B %d, %Y'),
            'total_petitions': total_petitions,
            'petitions_trend': ((total_petitions - prev_total) / prev_total * 100) if prev_total > 0 else 0,
            'resolution_rate': f"{resolution_rate:.1f}%",
            'resolution_trend': resolution_rate - prev_resolution_rate,
            'avg_response_time': avg_response_time,
            'response_trend': response_trend,
            'satisfaction_score': satisfaction_score,
            'satisfaction_trend': satisfaction_trend,
            'status_breakdown': status_breakdown,
            'insights': insights
        }
        
        # Generate HTML template
        html_content = get_weekly_report_template(report_data)
        
        # Send email
        send_email(
            to_email=dept_email,
            subject=f"📈 Weekly Performance Report - {department_name} - Week of {week_ago.strftime('%B %d')}",
            html_body=html_content
        )
        
        print(f"📧 Weekly report sent to {department_name} ({dept_email})")
        return True
        
    except Exception as e:
        print(f"❌ Error sending weekly report to {department_name}: {str(e)}")
        return False

# ============= REPORT TRIGGER APIs =============

@app.route('/api/reports/daily', methods=['POST'])
def trigger_daily_report():
    """Manually trigger daily report for the logged-in department"""
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authorized'}), 401
        
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Check if daily reports are enabled in preferences
        preferences = department.get('notification_preferences', {})
        if not preferences.get('daily_summary', True):
            return jsonify({'error': 'Daily reports are disabled in settings'}), 400
        
        dept_name = department['name']
        dept_email = department['email']
        
        # Send daily report
        success = send_daily_report(dept_name, dept_email)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Daily report sent to {dept_email}'
            }), 200
        else:
            return jsonify({'error': 'Failed to send daily report'}), 500
        
    except Exception as e:
        print(f"❌ Error triggering daily report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/weekly', methods=['POST'])
def trigger_weekly_report():
    """Manually trigger weekly report for the logged-in department"""
    try:
        if 'department_id' not in session:
            return jsonify({'error': 'Not authorized'}), 401
        
        dept_id = session['department_id']
        department = db.departments.find_one({'_id': ObjectId(dept_id)})
        
        if not department:
            return jsonify({'error': 'Department not found'}), 404
        
        # Check if weekly reports are enabled in preferences
        preferences = department.get('notification_preferences', {})
        if not preferences.get('weekly_report', True):
            return jsonify({'error': 'Weekly reports are disabled in settings'}), 400
        
        dept_name = department['name']
        dept_email = department['email']
        
        # Send weekly report
        success = send_weekly_report(dept_name, dept_email)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Weekly report sent to {dept_email}'
            }), 200
        else:
            return jsonify({'error': 'Failed to send weekly report'}), 500
        
    except Exception as e:
        print(f"❌ Error triggering weekly report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/send-all-daily', methods=['POST'])
def send_all_daily_reports():
    """Send daily reports to all departments (for scheduled task)"""
    try:
        # This endpoint could be protected with an API key for cron jobs
        departments = db.departments.find()
        
        sent_count = 0
        for dept in departments:
            preferences = dept.get('notification_preferences', {})
            if preferences.get('daily_summary', True):
                if send_daily_report(dept['name'], dept['email']):
                    sent_count += 1
        
        print(f"📧 Sent daily reports to {sent_count} departments")
        
        return jsonify({
            'success': True,
            'message': f'Sent daily reports to {sent_count} departments'
        }), 200
        
    except Exception as e:
        print(f"❌ Error sending all daily reports: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/send-all-weekly', methods=['POST'])
def send_all_weekly_reports():
    """Send weekly reports to all departments (for scheduled task)"""
    try:
        # This endpoint could be protected with an API key for cron jobs
        departments = db.departments.find()
        
        sent_count = 0
        for dept in departments:
            preferences = dept.get('notification_preferences', {})
            if preferences.get('weekly_report', True):
                if send_weekly_report(dept['name'], dept['email']):
                    sent_count += 1
        
        print(f"📧 Sent weekly reports to {sent_count} departments")
        
        return jsonify({
            'success': True,
            'message': f'Sent weekly reports to {sent_count} departments'
        }), 200
        
    except Exception as e:
        print(f"❌ Error sending all weekly reports: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)