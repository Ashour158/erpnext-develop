# Clean ERP System - Main Application
# Complete Flask application without Frappe dependencies

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_migrate import Migrate
import os
from datetime import datetime
import logging

# Import core components
from core.database import db, BaseModel, DatabaseManager
from core.auth import auth_manager, jwt_manager
from modules.crm import crm_bp
from modules.finance import finance_bp
from modules.people import people_bp
from modules.supply_chain import supply_chain_bp
from modules.maintenance import maintenance_bp
from modules.booking import booking_bp
from modules.moments import moments_bp
from core.system_settings_api import system_settings_bp

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://username:password@localhost/clean_erp_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Initialize extensions
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    db.init_app(app)
    migrate = Migrate(app, db)
    auth_manager.init_app(app)
    jwt_manager.init_app(app)
    
    # Initialize SocketIO for real-time features
    socketio = SocketIO(app, cors_allowed_origins=['http://localhost:3000'])
    
    # Register blueprints
    app.register_blueprint(crm_bp, url_prefix='/api/crm')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')
    app.register_blueprint(people_bp, url_prefix='/api/people')
    app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
    app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
    app.register_blueprint(booking_bp, url_prefix='/api/booking')
    app.register_blueprint(moments_bp, url_prefix='/api/moments')
    app.register_blueprint(system_settings_bp, url_prefix='/api/system-settings')
    
    # API Routes
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected'
        })
    
    @app.route('/api/status')
    def system_status():
        """System status endpoint"""
        return jsonify({
            'system': 'Clean ERP System',
            'version': '1.0.0',
            'status': 'operational',
            'modules': {
                'crm': 'active',
                'finance': 'active',
                'people': 'active',
                'supply_chain': 'active',
                'maintenance': 'active',
                'booking': 'active',
                'moments': 'active'
            },
            'features': {
                'real_time': True,
                'ai_analytics': True,
                'multi_company': True,
                'multi_currency': True,
                'mobile_support': True
            }
        })
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500
    
    # SocketIO Events
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f'Client connected: {request.sid}')
        emit('connected', {'message': 'Connected to Clean ERP System'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f'Client disconnected: {request.sid}')
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle joining a room"""
        room = data.get('room')
        if room:
            join_room(room)
            emit('joined_room', {'room': room})
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle leaving a room"""
        room = data.get('room')
        if room:
            leave_room(room)
            emit('left_room', {'room': room})
    
    @socketio.on('broadcast_update')
    def handle_broadcast_update(data):
        """Handle broadcasting updates"""
        room = data.get('room', 'global')
        emit('update', data, room=room)
    
    # Database initialization
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
    
    return app, socketio

# Create application instance
app, socketio = create_app()

if __name__ == '__main__':
    # Development server
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        allow_unsafe_werkzeug=True
    )
