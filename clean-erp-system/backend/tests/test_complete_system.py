# Complete System End-to-End Tests
# Comprehensive testing of all ERP modules and integrations

import pytest
import json
import requests
from datetime import datetime, date, timedelta
from core.database import db, init_db
from core.auth import create_user, authenticate_user
from modules.crm.models import Customer, Contact, Opportunity
from modules.finance.models import Company, Invoice, Payment
from modules.people.models import Employee, Department, LeaveRequest
from modules.supply_chain.models import Item, Supplier, PurchaseOrder
from modules.maintenance.models import Asset, WorkOrder
from modules.booking.models import Resource, Booking
from modules.moments.models import Moment, UserProfile
from modules.ai.models import AIModel, AIPrediction
from modules.workflow.models import Workflow, WorkflowExecution

class TestCompleteSystem:
    """Complete system integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Setup test environment"""
        with app.app_context():
            init_db()
            self.app = app
            self.client = app.test_client()
            self.base_url = 'http://localhost:5000'
    
    def test_system_health(self):
        """Test system health endpoints"""
        # Test backend health
        response = self.client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
        
        # Test database connectivity
        response = self.client.get('/api/health')
        assert response.status_code == 200
    
    def test_user_authentication(self):
        """Test user authentication flow"""
        # Create test user
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Register user
        response = self.client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        # Login user
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        assert 'token' in response.json
        
        return response.json['token']
    
    def test_crm_module_integration(self):
        """Test CRM module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create customer
        customer_data = {
            'customer_name': 'Test Customer',
            'email': 'customer@example.com',
            'phone': '+1234567890',
            'company_id': 1
        }
        response = self.client.post('/api/crm/customers', json=customer_data, headers=headers)
        assert response.status_code == 201
        customer_id = response.json['data']['id']
        
        # Create contact
        contact_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'customer_id': customer_id,
            'company_id': 1
        }
        response = self.client.post('/api/crm/contacts', json=contact_data, headers=headers)
        assert response.status_code == 201
        
        # Create opportunity
        opportunity_data = {
            'opportunity_name': 'Test Opportunity',
            'customer_id': customer_id,
            'expected_close_date': (date.today() + timedelta(days=30)).isoformat(),
            'expected_revenue': 10000.0,
            'company_id': 1
        }
        response = self.client.post('/api/crm/opportunities', json=opportunity_data, headers=headers)
        assert response.status_code == 201
        
        return customer_id
    
    def test_finance_module_integration(self):
        """Test Finance module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create company
        company_data = {
            'name': 'Test Company',
            'code': 'TC001',
            'email': 'company@example.com',
            'base_currency': 'USD'
        }
        response = self.client.post('/api/finance/companies', json=company_data, headers=headers)
        assert response.status_code == 201
        company_id = response.json['data']['id']
        
        # Create invoice
        invoice_data = {
            'invoice_number': 'INV-001',
            'invoice_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=30)).isoformat(),
            'customer_name': 'Test Customer',
            'subtotal': 1000.0,
            'tax_amount': 100.0,
            'total_amount': 1100.0,
            'company_id': company_id
        }
        response = self.client.post('/api/finance/invoices', json=invoice_data, headers=headers)
        assert response.status_code == 201
        invoice_id = response.json['data']['id']
        
        # Create payment
        payment_data = {
            'payment_number': 'PAY-001',
            'payment_date': date.today().isoformat(),
            'amount': 1100.0,
            'payment_method': 'Bank Transfer',
            'invoice_id': invoice_id,
            'company_id': company_id
        }
        response = self.client.post('/api/finance/payments', json=payment_data, headers=headers)
        assert response.status_code == 201
        
        return company_id, invoice_id
    
    def test_people_module_integration(self):
        """Test People module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create department
        department_data = {
            'name': 'Engineering',
            'code': 'ENG',
            'description': 'Engineering Department',
            'company_id': 1
        }
        response = self.client.post('/api/people/departments', json=department_data, headers=headers)
        assert response.status_code == 201
        department_id = response.json['data']['id']
        
        # Create employee
        employee_data = {
            'employee_id': 'EMP001',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'department_id': department_id,
            'date_of_joining': date.today().isoformat(),
            'company_id': 1
        }
        response = self.client.post('/api/people/employees', json=employee_data, headers=headers)
        assert response.status_code == 201
        employee_id = response.json['data']['id']
        
        # Create leave request
        leave_data = {
            'employee_id': employee_id,
            'leave_type_id': 1,
            'start_date': (date.today() + timedelta(days=7)).isoformat(),
            'end_date': (date.today() + timedelta(days=9)).isoformat(),
            'total_days': 3,
            'reason': 'Personal leave',
            'company_id': 1
        }
        response = self.client.post('/api/people/leave-requests', json=leave_data, headers=headers)
        assert response.status_code == 201
        
        return employee_id
    
    def test_supply_chain_module_integration(self):
        """Test Supply Chain module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create supplier
        supplier_data = {
            'supplier_name': 'Test Supplier',
            'supplier_code': 'SUP001',
            'email': 'supplier@example.com',
            'phone': '+1234567890',
            'company_id': 1
        }
        response = self.client.post('/api/supply-chain/suppliers', json=supplier_data, headers=headers)
        assert response.status_code == 201
        supplier_id = response.json['data']['id']
        
        # Create item
        item_data = {
            'item_name': 'Test Product',
            'item_code': 'PROD001',
            'description': 'Test product description',
            'item_type': 'Product',
            'standard_rate': 100.0,
            'company_id': 1
        }
        response = self.client.post('/api/supply-chain/items', json=item_data, headers=headers)
        assert response.status_code == 201
        item_id = response.json['data']['id']
        
        # Create purchase order
        po_data = {
            'order_number': 'PO-001',
            'order_date': date.today().isoformat(),
            'supplier_id': supplier_id,
            'item_id': item_id,
            'quantity': 10,
            'rate': 100.0,
            'amount': 1000.0,
            'company_id': 1
        }
        response = self.client.post('/api/supply-chain/purchase-orders', json=po_data, headers=headers)
        assert response.status_code == 201
        
        return item_id
    
    def test_maintenance_module_integration(self):
        """Test Maintenance module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create asset
        asset_data = {
            'asset_name': 'Test Asset',
            'asset_code': 'AST001',
            'description': 'Test asset description',
            'asset_category_id': 1,
            'purchase_cost': 5000.0,
            'company_id': 1
        }
        response = self.client.post('/api/maintenance/assets', json=asset_data, headers=headers)
        assert response.status_code == 201
        asset_id = response.json['data']['id']
        
        # Create work order
        work_order_data = {
            'work_order_number': 'WO-001',
            'work_order_date': datetime.now().isoformat(),
            'asset_id': asset_id,
            'title': 'Test Work Order',
            'description': 'Test work order description',
            'priority': 'Medium',
            'company_id': 1
        }
        response = self.client.post('/api/maintenance/work-orders', json=work_order_data, headers=headers)
        assert response.status_code == 201
        
        return asset_id
    
    def test_booking_module_integration(self):
        """Test Booking module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create resource
        resource_data = {
            'resource_name': 'Conference Room A',
            'resource_code': 'CR001',
            'description': 'Large conference room',
            'resource_type': 'Room',
            'capacity': 20,
            'company_id': 1
        }
        response = self.client.post('/api/booking/resources', json=resource_data, headers=headers)
        assert response.status_code == 201
        resource_id = response.json['data']['id']
        
        # Create booking
        booking_data = {
            'booking_number': 'BK-001',
            'booking_date': datetime.now().isoformat(),
            'resource_id': resource_id,
            'title': 'Team Meeting',
            'start_datetime': (datetime.now() + timedelta(days=1)).isoformat(),
            'end_datetime': (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            'company_id': 1
        }
        response = self.client.post('/api/booking/bookings', json=booking_data, headers=headers)
        assert response.status_code == 201
        
        return resource_id
    
    def test_moments_module_integration(self):
        """Test Moments module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create user profile
        profile_data = {
            'user_id': 1,
            'display_name': 'Test User',
            'bio': 'Test user bio',
            'company_id': 1
        }
        response = self.client.post('/api/moments/user-profiles', json=profile_data, headers=headers)
        assert response.status_code == 201
        
        # Create moment
        moment_data = {
            'author_id': 1,
            'content': 'Test moment content',
            'moment_type': 'Text',
            'visibility': 'Public',
            'company_id': 1
        }
        response = self.client.post('/api/moments/moments', json=moment_data, headers=headers)
        assert response.status_code == 201
        
        return response.json['data']['id']
    
    def test_ai_module_integration(self):
        """Test AI module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create AI model
        model_data = {
            'model_name': 'Test Model',
            'model_code': 'MODEL001',
            'description': 'Test AI model',
            'model_type': 'Predictive',
            'company_id': 1
        }
        response = self.client.post('/api/ai/ai-models', json=model_data, headers=headers)
        assert response.status_code == 201
        model_id = response.json['data']['id']
        
        # Create prediction
        prediction_data = {
            'model_id': model_id,
            'prediction_name': 'Test Prediction',
            'prediction_type': 'Sales Forecast',
            'input_data': {'sales_data': [100, 200, 300]},
            'predicted_value': 400.0,
            'confidence_score': 0.85,
            'company_id': 1
        }
        response = self.client.post('/api/ai/ai-predictions', json=prediction_data, headers=headers)
        assert response.status_code == 201
        
        return model_id
    
    def test_workflow_module_integration(self):
        """Test Workflow module functionality"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create workflow
        workflow_data = {
            'workflow_name': 'Test Workflow',
            'workflow_code': 'WF001',
            'description': 'Test workflow description',
            'workflow_type': 'Approval',
            'company_id': 1
        }
        response = self.client.post('/api/workflow/workflows', json=workflow_data, headers=headers)
        assert response.status_code == 201
        workflow_id = response.json['data']['id']
        
        # Create workflow execution
        execution_data = {
            'workflow_id': workflow_id,
            'execution_name': 'Test Execution',
            'input_data': {'test': 'data'},
            'company_id': 1
        }
        response = self.client.post('/api/workflow/workflow-executions', json=execution_data, headers=headers)
        assert response.status_code == 201
        
        return workflow_id
    
    def test_cross_module_integration(self):
        """Test integration between different modules"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create customer in CRM
        customer_id = self.test_crm_module_integration()
        
        # Create invoice in Finance linked to customer
        invoice_data = {
            'invoice_number': 'INV-002',
            'invoice_date': date.today().isoformat(),
            'customer_id': customer_id,
            'subtotal': 2000.0,
            'total_amount': 2000.0,
            'company_id': 1
        }
        response = self.client.post('/api/finance/invoices', json=invoice_data, headers=headers)
        assert response.status_code == 201
        
        # Create employee in People
        employee_id = self.test_people_module_integration()
        
        # Create asset in Maintenance assigned to employee
        asset_data = {
            'asset_name': 'Employee Asset',
            'asset_code': 'AST002',
            'custodian_id': employee_id,
            'purchase_cost': 3000.0,
            'company_id': 1
        }
        response = self.client.post('/api/maintenance/assets', json=asset_data, headers=headers)
        assert response.status_code == 201
        
        # Create booking for employee
        resource_id = self.test_booking_module_integration()
        booking_data = {
            'booking_number': 'BK-002',
            'booking_date': datetime.now().isoformat(),
            'resource_id': resource_id,
            'title': 'Employee Meeting',
            'booked_by_id': employee_id,
            'start_datetime': (datetime.now() + timedelta(days=2)).isoformat(),
            'end_datetime': (datetime.now() + timedelta(days=2, hours=1)).isoformat(),
            'company_id': 1
        }
        response = self.client.post('/api/booking/bookings', json=booking_data, headers=headers)
        assert response.status_code == 201
        
        return True
    
    def test_system_performance(self):
        """Test system performance under load"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test concurrent requests
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = self.client.get('/api/crm/customers', headers=headers)
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert all(result['status_code'] == 200 for result in results)
        
        # Check average response time
        avg_response_time = sum(result['response_time'] for result in results) / len(results)
        assert avg_response_time < 1.0  # Should be under 1 second
    
    def test_data_consistency(self):
        """Test data consistency across modules"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create customer
        customer_id = self.test_crm_module_integration()
        
        # Create invoice for customer
        invoice_data = {
            'invoice_number': 'INV-003',
            'invoice_date': date.today().isoformat(),
            'customer_id': customer_id,
            'subtotal': 1500.0,
            'total_amount': 1500.0,
            'company_id': 1
        }
        response = self.client.post('/api/finance/invoices', json=invoice_data, headers=headers)
        assert response.status_code == 201
        invoice_id = response.json['data']['id']
        
        # Verify customer exists in CRM
        response = self.client.get(f'/api/crm/customers/{customer_id}', headers=headers)
        assert response.status_code == 200
        
        # Verify invoice exists in Finance
        response = self.client.get(f'/api/finance/invoices/{invoice_id}', headers=headers)
        assert response.status_code == 200
        
        # Verify invoice is linked to customer
        invoice_data = response.json['data']
        assert invoice_data['customer_id'] == customer_id
    
    def test_error_handling(self):
        """Test error handling across modules"""
        token = self.test_user_authentication()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test invalid data
        invalid_customer_data = {
            'customer_name': '',  # Empty name should fail
            'email': 'invalid-email',  # Invalid email format
            'company_id': 1
        }
        response = self.client.post('/api/crm/customers', json=invalid_customer_data, headers=headers)
        assert response.status_code == 400
        
        # Test non-existent resource
        response = self.client.get('/api/crm/customers/99999', headers=headers)
        assert response.status_code == 404
        
        # Test unauthorized access
        response = self.client.get('/api/crm/customers')
        assert response.status_code == 401
    
    def test_system_recovery(self):
        """Test system recovery after failures"""
        # This would test database recovery, service restart, etc.
        # Implementation depends on specific failure scenarios
        pass
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality"""
        # This would test database backup and restore
        # Implementation depends on backup strategy
        pass

if __name__ == '__main__':
    pytest.main([__file__])

