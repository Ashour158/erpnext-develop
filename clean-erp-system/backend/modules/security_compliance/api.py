# Security & Compliance API
# API endpoints for security and compliance features including data privacy controls, audit trails, encryption, and access controls

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.database import db
from core.realtime_sync import emit_realtime_update
from .models import (
    AuditLog, DataPrivacyRule, DataRetentionPolicy, EncryptionKey,
    AccessControl, SecurityIncident, ComplianceReport, DataAnonymization,
    AuditAction, AuditLevel, DataClassification, EncryptionType, ComplianceStandard
)
from datetime import datetime, timedelta, date
import json

security_compliance_bp = Blueprint('security_compliance', __name__)

# Audit Logs
@security_compliance_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get audit logs"""
    try:
        company_id = request.args.get('company_id', type=int)
        action = request.args.get('action')
        audit_level = request.args.get('audit_level')
        entity_type = request.args.get('entity_type')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = AuditLog.query.filter(AuditLog.company_id == company_id)
        
        if action:
            query = query.filter(AuditLog.action == AuditAction(action))
        
        if audit_level:
            query = query.filter(AuditLog.audit_level == AuditLevel(audit_level))
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(AuditLog.created_at <= datetime.fromisoformat(end_date))
        
        logs = query.order_by(AuditLog.created_at.desc()).limit(1000).all()
        
        return jsonify([log.to_dict() for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/audit-logs', methods=['POST'])
@jwt_required()
def create_audit_log():
    """Create audit log"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['action', 'entity_type', 'entity_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create audit log
        audit_log = AuditLog(
            action=AuditAction(data['action']),
            action_description=data.get('action_description'),
            audit_level=AuditLevel(data.get('audit_level', 'MEDIUM')),
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            entity_name=data.get('entity_name'),
            user_id=data.get('user_id', user_id),
            user_ip=data.get('user_ip'),
            user_agent=data.get('user_agent'),
            session_id=data.get('session_id'),
            old_values=data.get('old_values'),
            new_values=data.get('new_values'),
            changed_fields=data.get('changed_fields'),
            metadata=data.get('metadata'),
            tags=data.get('tags'),
            company_id=data['company_id']
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('audit_log_created', audit_log.to_dict(), data['company_id'])
        
        return jsonify(audit_log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Data Privacy Rules
@security_compliance_bp.route('/privacy-rules', methods=['GET'])
@jwt_required()
def get_data_privacy_rules():
    """Get data privacy rules"""
    try:
        company_id = request.args.get('company_id', type=int)
        rule_type = request.args.get('rule_type')
        data_classification = request.args.get('data_classification')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DataPrivacyRule.query.filter(DataPrivacyRule.company_id == company_id)
        
        if rule_type:
            query = query.filter(DataPrivacyRule.rule_type == rule_type)
        
        if data_classification:
            query = query.filter(DataPrivacyRule.data_classification == DataClassification(data_classification))
        
        if is_active is not None:
            query = query.filter(DataPrivacyRule.is_active == is_active)
        
        rules = query.order_by(DataPrivacyRule.created_at.desc()).all()
        
        return jsonify([rule.to_dict() for rule in rules])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/privacy-rules', methods=['POST'])
@jwt_required()
def create_data_privacy_rule():
    """Create data privacy rule"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['rule_name', 'rule_type', 'data_classification', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create rule
        rule = DataPrivacyRule(
            rule_name=data['rule_name'],
            rule_description=data.get('rule_description'),
            rule_type=data['rule_type'],
            is_active=data.get('is_active', True),
            data_classification=DataClassification(data['data_classification']),
            data_types=data.get('data_types'),
            data_fields=data.get('data_fields'),
            rule_config=data.get('rule_config'),
            retention_period=data.get('retention_period', 0),
            anonymization_method=data.get('anonymization_method'),
            encryption_required=data.get('encryption_required', False),
            compliance_standards=data.get('compliance_standards'),
            legal_basis=data.get('legal_basis'),
            consent_required=data.get('consent_required', False),
            company_id=data['company_id']
        )
        
        db.session.add(rule)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('data_privacy_rule_created', rule.to_dict(), data['company_id'])
        
        return jsonify(rule.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Data Retention Policies
@security_compliance_bp.route('/retention-policies', methods=['GET'])
@jwt_required()
def get_data_retention_policies():
    """Get data retention policies"""
    try:
        company_id = request.args.get('company_id', type=int)
        data_classification = request.args.get('data_classification')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DataRetentionPolicy.query.filter(DataRetentionPolicy.company_id == company_id)
        
        if data_classification:
            query = query.filter(DataRetentionPolicy.data_classification == DataClassification(data_classification))
        
        if is_active is not None:
            query = query.filter(DataRetentionPolicy.is_active == is_active)
        
        policies = query.order_by(DataRetentionPolicy.created_at.desc()).all()
        
        return jsonify([policy.to_dict() for policy in policies])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/retention-policies', methods=['POST'])
@jwt_required()
def create_data_retention_policy():
    """Create data retention policy"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['policy_name', 'data_classification', 'retention_period', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create policy
        policy = DataRetentionPolicy(
            policy_name=data['policy_name'],
            policy_description=data.get('policy_description'),
            is_active=data.get('is_active', True),
            data_types=data.get('data_types'),
            data_classification=DataClassification(data['data_classification']),
            entity_types=data.get('entity_types'),
            retention_period=data['retention_period'],
            retention_unit=data.get('retention_unit', 'days'),
            auto_delete=data.get('auto_delete', False),
            archive_before_delete=data.get('archive_before_delete', True),
            compliance_standards=data.get('compliance_standards'),
            legal_requirements=data.get('legal_requirements'),
            company_id=data['company_id']
        )
        
        db.session.add(policy)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('data_retention_policy_created', policy.to_dict(), data['company_id'])
        
        return jsonify(policy.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Encryption Keys
@security_compliance_bp.route('/encryption-keys', methods=['GET'])
@jwt_required()
def get_encryption_keys():
    """Get encryption keys"""
    try:
        company_id = request.args.get('company_id', type=int)
        key_type = request.args.get('key_type')
        is_active = request.args.get('is_active', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = EncryptionKey.query.filter(EncryptionKey.company_id == company_id)
        
        if key_type:
            query = query.filter(EncryptionKey.key_type == EncryptionType(key_type))
        
        if is_active is not None:
            query = query.filter(EncryptionKey.is_active == is_active)
        
        keys = query.order_by(EncryptionKey.created_at.desc()).all()
        
        return jsonify([key.to_dict() for key in keys])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/encryption-keys', methods=['POST'])
@jwt_required()
def create_encryption_key():
    """Create encryption key"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['key_name', 'key_type', 'key_data', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create key
        key = EncryptionKey(
            key_name=data['key_name'],
            key_description=data.get('key_description'),
            key_type=EncryptionType(data['key_type']),
            key_size=data.get('key_size', 256),
            key_data=data['key_data'],
            key_hash=data.get('key_hash'),
            is_active=data.get('is_active', True),
            created_by=user_id,
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            usage_count=data.get('usage_count', 0),
            max_usage=data.get('max_usage', 0),
            company_id=data['company_id']
        )
        
        db.session.add(key)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('encryption_key_created', key.to_dict(), data['company_id'])
        
        return jsonify(key.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Access Controls
@security_compliance_bp.route('/access-controls', methods=['GET'])
@jwt_required()
def get_access_controls():
    """Get access controls"""
    try:
        company_id = request.args.get('company_id', type=int)
        resource_type = request.args.get('resource_type')
        user_id = request.args.get('user_id', type=int)
        role_id = request.args.get('role_id', type=int)
        is_granted = request.args.get('is_granted', type=bool)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = AccessControl.query.filter(AccessControl.company_id == company_id)
        
        if resource_type:
            query = query.filter(AccessControl.resource_type == resource_type)
        
        if user_id:
            query = query.filter(AccessControl.user_id == user_id)
        
        if role_id:
            query = query.filter(AccessControl.role_id == role_id)
        
        if is_granted is not None:
            query = query.filter(AccessControl.is_granted == is_granted)
        
        controls = query.order_by(AccessControl.created_at.desc()).all()
        
        return jsonify([control.to_dict() for control in controls])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/access-controls', methods=['POST'])
@jwt_required()
def create_access_control():
    """Create access control"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['resource_type', 'resource_id', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create access control
        control = AccessControl(
            resource_type=data['resource_type'],
            resource_id=data['resource_id'],
            resource_name=data.get('resource_name'),
            user_id=data.get('user_id'),
            role_id=data.get('role_id'),
            permissions=data.get('permissions'),
            access_level=data.get('access_level', 'Read'),
            is_granted=data.get('is_granted', True),
            ip_restrictions=data.get('ip_restrictions'),
            time_restrictions=data.get('time_restrictions'),
            location_restrictions=data.get('location_restrictions'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            is_temporary=data.get('is_temporary', False),
            company_id=data['company_id']
        )
        
        db.session.add(control)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('access_control_created', control.to_dict(), data['company_id'])
        
        return jsonify(control.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Security Incidents
@security_compliance_bp.route('/security-incidents', methods=['GET'])
@jwt_required()
def get_security_incidents():
    """Get security incidents"""
    try:
        company_id = request.args.get('company_id', type=int)
        incident_type = request.args.get('incident_type')
        severity = request.args.get('severity')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = SecurityIncident.query.filter(SecurityIncident.company_id == company_id)
        
        if incident_type:
            query = query.filter(SecurityIncident.incident_type == incident_type)
        
        if severity:
            query = query.filter(SecurityIncident.severity == AuditLevel(severity))
        
        if status:
            query = query.filter(SecurityIncident.status == status)
        
        if start_date:
            query = query.filter(SecurityIncident.incident_date >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(SecurityIncident.incident_date <= datetime.fromisoformat(end_date))
        
        incidents = query.order_by(SecurityIncident.incident_date.desc()).all()
        
        return jsonify([incident.to_dict() for incident in incidents])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/security-incidents', methods=['POST'])
@jwt_required()
def create_security_incident():
    """Create security incident"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['incident_title', 'incident_type', 'severity', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create incident
        incident = SecurityIncident(
            incident_title=data['incident_title'],
            incident_description=data.get('incident_description'),
            incident_type=data['incident_type'],
            severity=AuditLevel(data['severity']),
            incident_date=datetime.fromisoformat(data['incident_date']) if data.get('incident_date') else datetime.utcnow(),
            discovered_by=data.get('discovered_by', user_id),
            affected_users=data.get('affected_users'),
            affected_data=data.get('affected_data'),
            status=data.get('status', 'Open'),
            assigned_to=data.get('assigned_to'),
            resolution_notes=data.get('resolution_notes'),
            resolved_at=datetime.fromisoformat(data['resolved_at']) if data.get('resolved_at') else None,
            impact_level=data.get('impact_level', 'Low'),
            data_compromised=data.get('data_compromised', False),
            systems_affected=data.get('systems_affected'),
            company_id=data['company_id']
        )
        
        db.session.add(incident)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('security_incident_created', incident.to_dict(), data['company_id'])
        
        return jsonify(incident.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Compliance Reports
@security_compliance_bp.route('/compliance-reports', methods=['GET'])
@jwt_required()
def get_compliance_reports():
    """Get compliance reports"""
    try:
        company_id = request.args.get('company_id', type=int)
        compliance_standard = request.args.get('compliance_standard')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = ComplianceReport.query.filter(ComplianceReport.company_id == company_id)
        
        if compliance_standard:
            query = query.filter(ComplianceReport.compliance_standard == ComplianceStandard(compliance_standard))
        
        if status:
            query = query.filter(ComplianceReport.status == status)
        
        if start_date:
            query = query.filter(ComplianceReport.report_period_start >= date.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(ComplianceReport.report_period_end <= date.fromisoformat(end_date))
        
        reports = query.order_by(ComplianceReport.generated_at.desc()).all()
        
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/compliance-reports', methods=['POST'])
@jwt_required()
def create_compliance_report():
    """Create compliance report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['report_name', 'compliance_standard', 'report_period_start', 'report_period_end', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create report
        report = ComplianceReport(
            report_name=data['report_name'],
            report_description=data.get('report_description'),
            compliance_standard=ComplianceStandard(data['compliance_standard']),
            report_period_start=date.fromisoformat(data['report_period_start']),
            report_period_end=date.fromisoformat(data['report_period_end']),
            status=data.get('status', 'Draft'),
            generated_by=user_id,
            report_data=data.get('report_data'),
            findings=data.get('findings'),
            recommendations=data.get('recommendations'),
            violations=data.get('violations'),
            company_id=data['company_id']
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('compliance_report_created', report.to_dict(), data['company_id'])
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Data Anonymization
@security_compliance_bp.route('/data-anonymization', methods=['GET'])
@jwt_required()
def get_data_anonymizations():
    """Get data anonymizations"""
    try:
        company_id = request.args.get('company_id', type=int)
        data_type = request.args.get('data_type')
        data_classification = request.args.get('data_classification')
        anonymization_method = request.args.get('anonymization_method')
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        query = DataAnonymization.query.filter(DataAnonymization.company_id == company_id)
        
        if data_type:
            query = query.filter(DataAnonymization.data_type == data_type)
        
        if data_classification:
            query = query.filter(DataAnonymization.data_classification == DataClassification(data_classification))
        
        if anonymization_method:
            query = query.filter(DataAnonymization.anonymization_method == anonymization_method)
        
        anonymizations = query.order_by(DataAnonymization.anonymization_date.desc()).all()
        
        return jsonify([anonymization.to_dict() for anonymization in anonymizations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@security_compliance_bp.route('/data-anonymization', methods=['POST'])
@jwt_required()
def create_data_anonymization():
    """Create data anonymization"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['anonymization_name', 'anonymization_method', 'data_type', 'data_classification', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create anonymization
        anonymization = DataAnonymization(
            anonymization_name=data['anonymization_name'],
            anonymization_description=data.get('anonymization_description'),
            anonymization_method=data['anonymization_method'],
            data_type=data['data_type'],
            data_classification=DataClassification(data['data_classification']),
            original_data=data.get('original_data'),
            anonymized_data=data.get('anonymized_data'),
            anonymization_config=data.get('anonymization_config'),
            anonymized_by=user_id,
            company_id=data['company_id']
        )
        
        db.session.add(anonymization)
        db.session.commit()
        
        # Emit real-time update
        emit_realtime_update('data_anonymization_created', anonymization.to_dict(), data['company_id'])
        
        return jsonify(anonymization.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
