# Booking API - Complete Resource Booking and Scheduling API
# Advanced booking operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Resource, ResourceCategory, Booking, BookingSlot, BookingRule,
    RecurringBooking, BookingConflict, BookingApproval
)
from datetime import datetime, date, timedelta
import json

booking_api = Blueprint('booking_api', __name__)

# Resource Category Management
@booking_api.route('/resource-categories', methods=['GET'])
@token_required
def get_resource_categories():
    """Get all resource categories"""
    try:
        company_id = request.args.get('company_id')
        categories = ResourceCategory.query.filter_by(company_id=company_id).all()
        return jsonify({
            'success': True,
            'data': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/resource-categories', methods=['POST'])
@token_required
def create_resource_category():
    """Create new resource category"""
    try:
        data = request.get_json()
        category = ResourceCategory(
            category_name=data['category_name'],
            category_code=data['category_code'],
            description=data.get('description'),
            booking_advance_days=data.get('booking_advance_days', 30),
            cancellation_hours=data.get('cancellation_hours', 24),
            requires_approval=data.get('requires_approval', False),
            max_booking_duration_hours=data.get('max_booking_duration_hours', 24.0),
            company_id=data['company_id']
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'success': True, 'data': category.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Resource Management
@booking_api.route('/resources', methods=['GET'])
@token_required
def get_resources():
    """Get all resources"""
    try:
        company_id = request.args.get('company_id')
        category_id = request.args.get('category_id')
        resource_type = request.args.get('resource_type')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = Resource.query.filter_by(company_id=company_id)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        if is_active:
            query = query.filter_by(is_active=True)
        
        resources = query.all()
        return jsonify({
            'success': True,
            'data': [resource.to_dict() for resource in resources]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/resources', methods=['POST'])
@token_required
def create_resource():
    """Create new resource"""
    try:
        data = request.get_json()
        resource = Resource(
            resource_name=data['resource_name'],
            resource_code=data['resource_code'],
            description=data.get('description'),
            resource_type=data['resource_type'],
            category_id=data['category_id'],
            location=data.get('location'),
            address=data.get('address'),
            capacity=data.get('capacity', 1),
            is_active=data.get('is_active', True),
            is_bookable=data.get('is_bookable', True),
            requires_approval=data.get('requires_approval', False),
            hourly_rate=data.get('hourly_rate', 0),
            daily_rate=data.get('daily_rate', 0),
            currency=data.get('currency', 'USD'),
            available_from_time=data.get('available_from_time', '09:00'),
            available_to_time=data.get('available_to_time', '17:00'),
            available_days=data.get('available_days', [1,2,3,4,5]),
            features=data.get('features', []),
            images=data.get('images', []),
            company_id=data['company_id']
        )
        db.session.add(resource)
        db.session.commit()
        return jsonify({'success': True, 'data': resource.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/resources/<int:resource_id>', methods=['GET'])
@token_required
def get_resource(resource_id):
    """Get specific resource"""
    try:
        resource = Resource.query.get_or_404(resource_id)
        return jsonify({'success': True, 'data': resource.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Booking Management
@booking_api.route('/bookings', methods=['GET'])
@token_required
def get_bookings():
    """Get bookings"""
    try:
        company_id = request.args.get('company_id')
        resource_id = request.args.get('resource_id')
        booked_by_id = request.args.get('booked_by_id')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Booking.query.filter_by(company_id=company_id)
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        if booked_by_id:
            query = query.filter_by(booked_by_id=booked_by_id)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(Booking.start_datetime >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(Booking.end_datetime <= datetime.fromisoformat(end_date))
        
        bookings = query.all()
        return jsonify({
            'success': True,
            'data': [booking.to_dict() for booking in bookings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/bookings', methods=['POST'])
@token_required
def create_booking():
    """Create booking"""
    try:
        data = request.get_json()
        booking = Booking(
            booking_number=data['booking_number'],
            booking_date=datetime.fromisoformat(data['booking_date']),
            resource_id=data['resource_id'],
            title=data['title'],
            description=data.get('description'),
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            end_datetime=datetime.fromisoformat(data['end_datetime']),
            duration_hours=data.get('duration_hours', 0),
            booked_by_id=data.get('booked_by_id'),
            attendees=data.get('attendees', []),
            expected_attendees=data.get('expected_attendees', 1),
            priority=data.get('priority', 'Medium'),
            is_recurring=data.get('is_recurring', False),
            recurrence_type=data.get('recurrence_type', 'None'),
            recurrence_end_date=datetime.fromisoformat(data['recurrence_end_date']).date() if data.get('recurrence_end_date') else None,
            total_cost=data.get('total_cost', 0),
            currency=data.get('currency', 'USD'),
            special_requirements=data.get('special_requirements'),
            setup_notes=data.get('setup_notes'),
            company_id=data['company_id']
        )
        db.session.add(booking)
        db.session.commit()
        return jsonify({'success': True, 'data': booking.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/bookings/<int:booking_id>', methods=['GET'])
@token_required
def get_booking(booking_id):
    """Get specific booking"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        return jsonify({'success': True, 'data': booking.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@token_required
def cancel_booking(booking_id):
    """Cancel booking"""
    try:
        data = request.get_json()
        booking = Booking.query.get_or_404(booking_id)
        booking.status = 'Cancelled'
        booking.cancellation_reason = data.get('cancellation_reason')
        db.session.commit()
        return jsonify({'success': True, 'data': booking.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Booking Slot Management
@booking_api.route('/booking-slots', methods=['GET'])
@token_required
def get_booking_slots():
    """Get booking slots"""
    try:
        company_id = request.args.get('company_id')
        resource_id = request.args.get('resource_id')
        slot_date = request.args.get('slot_date')
        is_available = request.args.get('is_available')
        
        query = BookingSlot.query.filter_by(company_id=company_id)
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        if slot_date:
            query = query.filter_by(slot_date=datetime.fromisoformat(slot_date).date())
        if is_available:
            query = query.filter_by(is_available=is_available.lower() == 'true')
        
        slots = query.all()
        return jsonify({
            'success': True,
            'data': [slot.to_dict() for slot in slots]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/booking-slots', methods=['POST'])
@token_required
def create_booking_slot():
    """Create booking slot"""
    try:
        data = request.get_json()
        slot = BookingSlot(
            resource_id=data['resource_id'],
            booking_id=data.get('booking_id'),
            slot_date=datetime.fromisoformat(data['slot_date']).date(),
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_available=data.get('is_available', True),
            is_blocked=data.get('is_blocked', False),
            block_reason=data.get('block_reason'),
            company_id=data['company_id']
        )
        db.session.add(slot)
        db.session.commit()
        return jsonify({'success': True, 'data': slot.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Resource Availability
@booking_api.route('/resources/<int:resource_id>/availability', methods=['GET'])
@token_required
def get_resource_availability(resource_id):
    """Get resource availability"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Start date and end date are required'}), 400
        
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
        
        # Get existing bookings for the resource in the date range
        bookings = Booking.query.filter(
            Booking.resource_id == resource_id,
            Booking.start_datetime >= datetime.combine(start_date, datetime.min.time()),
            Booking.end_datetime <= datetime.combine(end_date, datetime.max.time()),
            Booking.status.in_(['Confirmed', 'Pending'])
        ).all()
        
        # Generate availability slots
        availability = []
        current_date = start_date
        while current_date <= end_date:
            # Check if resource is available on this day
            resource = Resource.query.get(resource_id)
            if resource and current_date.weekday() + 1 in resource.available_days:
                availability.append({
                    'date': current_date.isoformat(),
                    'available': True,
                    'bookings': [booking.to_dict() for booking in bookings if booking.start_datetime.date() == current_date]
                })
            else:
                availability.append({
                    'date': current_date.isoformat(),
                    'available': False,
                    'bookings': []
                })
            current_date += timedelta(days=1)
        
        return jsonify({'success': True, 'data': availability})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Booking Rules Management
@booking_api.route('/booking-rules', methods=['GET'])
@token_required
def get_booking_rules():
    """Get booking rules"""
    try:
        company_id = request.args.get('company_id')
        rule_type = request.args.get('rule_type')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = BookingRule.query.filter_by(company_id=company_id)
        if rule_type:
            query = query.filter_by(rule_type=rule_type)
        if is_active:
            query = query.filter_by(is_active=True)
        
        rules = query.all()
        return jsonify({
            'success': True,
            'data': [rule.to_dict() for rule in rules]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/booking-rules', methods=['POST'])
@token_required
def create_booking_rule():
    """Create booking rule"""
    try:
        data = request.get_json()
        rule = BookingRule(
            rule_name=data['rule_name'],
            rule_type=data['rule_type'],
            description=data.get('description'),
            conditions=data.get('conditions', {}),
            is_active=data.get('is_active', True),
            actions=data.get('actions', {}),
            company_id=data['company_id']
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({'success': True, 'data': rule.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Recurring Booking Management
@booking_api.route('/recurring-bookings', methods=['GET'])
@token_required
def get_recurring_bookings():
    """Get recurring bookings"""
    try:
        company_id = request.args.get('company_id')
        booking_id = request.args.get('booking_id')
        recurrence_type = request.args.get('recurrence_type')
        
        query = RecurringBooking.query.filter_by(company_id=company_id)
        if booking_id:
            query = query.filter_by(booking_id=booking_id)
        if recurrence_type:
            query = query.filter_by(recurrence_type=recurrence_type)
        
        recurring_bookings = query.all()
        return jsonify({
            'success': True,
            'data': [recurring.to_dict() for recurring in recurring_bookings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/recurring-bookings', methods=['POST'])
@token_required
def create_recurring_booking():
    """Create recurring booking"""
    try:
        data = request.get_json()
        recurring = RecurringBooking(
            booking_id=data['booking_id'],
            recurrence_type=data['recurrence_type'],
            recurrence_interval=data.get('recurrence_interval', 1),
            recurrence_end_date=datetime.fromisoformat(data['recurrence_end_date']).date() if data.get('recurrence_end_date') else None,
            max_occurrences=data.get('max_occurrences', 0),
            company_id=data['company_id']
        )
        db.session.add(recurring)
        db.session.commit()
        return jsonify({'success': True, 'data': recurring.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Booking Conflict Management
@booking_api.route('/booking-conflicts', methods=['GET'])
@token_required
def get_booking_conflicts():
    """Get booking conflicts"""
    try:
        company_id = request.args.get('company_id')
        booking_id = request.args.get('booking_id')
        is_resolved = request.args.get('is_resolved')
        
        query = BookingConflict.query.filter_by(company_id=company_id)
        if booking_id:
            query = query.filter_by(booking_id=booking_id)
        if is_resolved:
            query = query.filter_by(is_resolved=is_resolved.lower() == 'true')
        
        conflicts = query.all()
        return jsonify({
            'success': True,
            'data': [conflict.to_dict() for conflict in conflicts]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Booking Approval Management
@booking_api.route('/booking-approvals', methods=['GET'])
@token_required
def get_booking_approvals():
    """Get booking approvals"""
    try:
        company_id = request.args.get('company_id')
        booking_id = request.args.get('booking_id')
        approver_id = request.args.get('approver_id')
        approval_status = request.args.get('approval_status')
        
        query = BookingApproval.query.filter_by(company_id=company_id)
        if booking_id:
            query = query.filter_by(booking_id=booking_id)
        if approver_id:
            query = query.filter_by(approver_id=approver_id)
        if approval_status:
            query = query.filter_by(approval_status=approval_status)
        
        approvals = query.all()
        return jsonify({
            'success': True,
            'data': [approval.to_dict() for approval in approvals]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/booking-approvals', methods=['POST'])
@token_required
def create_booking_approval():
    """Create booking approval"""
    try:
        data = request.get_json()
        approval = BookingApproval(
            booking_id=data['booking_id'],
            approver_id=data['approver_id'],
            approval_status=data.get('approval_status', 'Pending'),
            approval_notes=data.get('approval_notes'),
            company_id=data['company_id']
        )
        db.session.add(approval)
        db.session.commit()
        return jsonify({'success': True, 'data': approval.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@booking_api.route('/booking-approvals/<int:approval_id>/approve', methods=['POST'])
@token_required
def approve_booking(approval_id):
    """Approve booking"""
    try:
        data = request.get_json()
        approval = BookingApproval.query.get_or_404(approval_id)
        approval.approval_status = 'Approved'
        approval.approval_date = datetime.now()
        approval.approval_notes = data.get('approval_notes')
        
        # Update booking status
        booking = Booking.query.get(approval.booking_id)
        if booking:
            booking.status = 'Confirmed'
        
        db.session.commit()
        return jsonify({'success': True, 'data': approval.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Booking Analytics
@booking_api.route('/booking-analytics', methods=['GET'])
@token_required
def get_booking_analytics():
    """Get booking analytics"""
    try:
        company_id = request.args.get('company_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Calculate analytics
        total_bookings = Booking.query.filter_by(company_id=company_id).count()
        confirmed_bookings = Booking.query.filter_by(company_id=company_id, status='Confirmed').count()
        cancelled_bookings = Booking.query.filter_by(company_id=company_id, status='Cancelled').count()
        
        total_resources = Resource.query.filter_by(company_id=company_id).count()
        active_resources = Resource.query.filter_by(company_id=company_id, is_active=True).count()
        
        analytics = {
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'booking_success_rate': (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0,
            'total_resources': total_resources,
            'active_resources': active_resources,
            'resource_utilization': (confirmed_bookings / active_resources) if active_resources > 0 else 0
        }
        
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
