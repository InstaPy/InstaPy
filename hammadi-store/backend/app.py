from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db, bcrypt, User, Category, Service, Order, PaymentRequest, APIProvider
from api_service import SMSAPIService
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Initialize database and create admin user
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='mk1707465@gmail.com').first()
    if not admin:
        admin = User(
            email='mk1707465@gmail.com',
            is_admin=True
        )
        admin.set_password('momomomomo2009')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    
    # Create default categories if not exist
    if Category.query.count() == 0:
        categories = [
            Category(name_ar='إنستغرام', name_en='Instagram', icon='instagram', order=1),
            Category(name_ar='تيك توك', name_en='TikTok', icon='tiktok', order=2),
            Category(name_ar='يوتيوب', name_en='YouTube', icon='youtube', order=3),
            Category(name_ar='سناب شات', name_en='Snapchat', icon='snapchat', order=4),
            Category(name_ar='تيلغرام', name_en='Telegram', icon='telegram', order=5),
            Category(name_ar='تويتر', name_en='Twitter', icon='twitter', order=6),
            Category(name_ar='فيسبوك', name_en='Facebook', icon='facebook', order=7),
            Category(name_ar='واتساب', name_en='WhatsApp', icon='whatsapp', order=8),
        ]
        db.session.add_all(categories)
        db.session.commit()
        print("Default categories created!")


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


# ==================== CATEGORY ROUTES ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by(is_active=True).order_by(Category.order).all()
    return jsonify({'categories': [cat.to_dict() for cat in categories]}), 200


# ==================== SERVICE ROUTES ====================

@app.route('/api/services', methods=['GET'])
def get_services():
    category_id = request.args.get('category_id', type=int)
    
    query = Service.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    services = query.all()
    return jsonify({'services': [service.to_dict() for service in services]}), 200


@app.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get(service_id)
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    return jsonify({'service': service.to_dict()}), 200


# ==================== ORDER ROUTES ====================

@app.route('/api/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()
    
    if not data or not all(k in data for k in ['service_id', 'link', 'quantity']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    service = Service.query.get(data['service_id'])
    if not service or not service.is_active:
        return jsonify({'error': 'Service not found or inactive'}), 404
    
    quantity = int(data['quantity'])
    
    if quantity < service.min_quantity or quantity > service.max_quantity:
        return jsonify({'error': f'Quantity must be between {service.min_quantity} and {service.max_quantity}'}), 400
    
    # Calculate price
    price = (quantity / 1000) * service.price_per_1000
    
    if user.balance < price:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Create order
    order = Order(
        user_id=user_id,
        service_id=service.id,
        link=data['link'],
        quantity=quantity,
        price=price,
        status='pending'
    )
    
    # Deduct balance
    user.balance -= price
    user.total_spent += price
    
    db.session.add(order)
    db.session.commit()
    
    # Try to submit to external API if configured
    if service.api_provider_id:
        result = SMSAPIService.create_order(order.id)
        if 'error' in result:
            order.status = 'pending'
            db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order.to_dict()
    }), 201


@app.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.is_admin:
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    return jsonify({'orders': [order.to_dict() for order in orders]}), 200


@app.route('/api/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if not user.is_admin and order.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({'order': order.to_dict()}), 200


# ==================== PAYMENT ROUTES ====================

@app.route('/api/payments/request', methods=['POST'])
@jwt_required()
def create_payment_request():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not all(k in data for k in ['payment_method', 'phone_number', 'amount']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['payment_method'] not in ['libyana', 'madar']:
        return jsonify({'error': 'Invalid payment method'}), 400
    
    amount = float(data['amount'])
    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than 0'}), 400
    
    payment_request = PaymentRequest(
        user_id=user_id,
        payment_method=data['payment_method'],
        phone_number=data['phone_number'],
        amount=amount,
        status='pending'
    )
    
    db.session.add(payment_request)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment request submitted successfully',
        'payment_request': payment_request.to_dict()
    }), 201


@app.route('/api/payments', methods=['GET'])
@jwt_required()
def get_payment_requests():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user.is_admin:
        payments = PaymentRequest.query.order_by(PaymentRequest.created_at.desc()).all()
    else:
        payments = PaymentRequest.query.filter_by(user_id=user_id).order_by(PaymentRequest.created_at.desc()).all()
    
    return jsonify({'payments': [payment.to_dict() for payment in payments]}), 200


# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    users = User.query.all()
    return jsonify({'users': [u.to_dict() for u in users]}), 200


@app.route('/api/admin/users/<int:target_user_id>/balance', methods=['POST'])
@jwt_required()
def update_user_balance(target_user_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    target_user = User.query.get(target_user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    if 'amount' not in data:
        return jsonify({'error': 'Amount is required'}), 400
    
    amount = float(data['amount'])
    target_user.balance += amount
    
    db.session.commit()
    
    return jsonify({
        'message': 'Balance updated successfully',
        'user': target_user.to_dict()
    }), 200


@app.route('/api/admin/payments/<int:payment_id>/approve', methods=['POST'])
@jwt_required()
def approve_payment(payment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    payment = PaymentRequest.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment request not found'}), 404
    
    if payment.status != 'pending':
        return jsonify({'error': 'Payment already processed'}), 400
    
    # Add balance to user
    payment.user.balance += payment.amount
    payment.status = 'approved'
    payment.processed_at = datetime.utcnow()
    
    data = request.get_json()
    if data and 'admin_note' in data:
        payment.admin_note = data['admin_note']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment approved successfully',
        'payment': payment.to_dict()
    }), 200


@app.route('/api/admin/payments/<int:payment_id>/reject', methods=['POST'])
@jwt_required()
def reject_payment(payment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    payment = PaymentRequest.query.get(payment_id)
    if not payment:
        return jsonify({'error': 'Payment request not found'}), 404
    
    if payment.status != 'pending':
        return jsonify({'error': 'Payment already processed'}), 400
    
    payment.status = 'rejected'
    payment.processed_at = datetime.utcnow()
    
    data = request.get_json()
    if data and 'admin_note' in data:
        payment.admin_note = data['admin_note']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment rejected',
        'payment': payment.to_dict()
    }), 200


@app.route('/api/admin/orders/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    if order.status == 'completed':
        return jsonify({'error': 'Cannot cancel completed order'}), 400
    
    # Refund user
    order.user.balance += order.price
    order.user.total_spent -= order.price
    order.status = 'canceled'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Order canceled and refunded',
        'order': order.to_dict()
    }), 200


@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    total_users = User.query.count()
    total_orders = Order.query.count()
    pending_payments = PaymentRequest.query.filter_by(status='pending').count()
    total_revenue = db.session.query(db.func.sum(Order.price)).scalar() or 0
    
    return jsonify({
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue
    }), 200


# ==================== API PROVIDER ROUTES ====================

@app.route('/api/admin/providers', methods=['GET'])
@jwt_required()
def get_providers():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    providers = APIProvider.query.all()
    return jsonify({'providers': [p.to_dict() for p in providers]}), 200


@app.route('/api/admin/providers', methods=['POST'])
@jwt_required()
def create_provider():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ['name', 'api_url', 'api_key']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    provider = APIProvider(
        name=data['name'],
        api_url=data['api_url'],
        api_key=data['api_key'],
        priority=data.get('priority', 0)
    )
    
    db.session.add(provider)
    db.session.commit()
    
    return jsonify({
        'message': 'Provider created successfully',
        'provider': provider.to_dict()
    }), 201


@app.route('/api/admin/services', methods=['POST'])
@jwt_required()
def create_service():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    required_fields = ['category_id', 'name_ar', 'name_en', 'price_per_1000']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    service = Service(
        category_id=data['category_id'],
        name_ar=data['name_ar'],
        name_en=data['name_en'],
        description_ar=data.get('description_ar', ''),
        description_en=data.get('description_en', ''),
        price_per_1000=float(data['price_per_1000']),
        min_quantity=int(data.get('min_quantity', 100)),
        max_quantity=int(data.get('max_quantity', 100000)),
        api_provider_id=data.get('api_provider_id'),
        external_service_id=data.get('external_service_id')
    )
    
    db.session.add(service)
    db.session.commit()
    
    return jsonify({
        'message': 'Service created successfully',
        'service': service.to_dict()
    }), 201


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'libyana_number': Config.LIBYANA_NUMBER,
        'madar_number': Config.MADAR_NUMBER,
        'whatsapp_number': Config.WHATSAPP_NUMBER,
        'telegram_channel': Config.TELEGRAM_CHANNEL
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
