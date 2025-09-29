# Comprehensive System Testing
# Complete testing of database, data flow, failure events, notifications, and edge cases

import pytest
import asyncio
import json
import time
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from unittest.mock import Mock, patch, MagicMock
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveSystemTester:
    """
    Comprehensive System Testing Suite
    Tests database, data flow, failure events, notifications, and edge cases
    """
    
    def __init__(self):
        self.test_results = {
            'database_tests': [],
            'data_flow_tests': [],
            'failure_tests': [],
            'notification_tests': [],
            'performance_tests': [],
            'security_tests': [],
            'integration_tests': [],
            'edge_case_tests': []
        }
        self.base_url = "http://localhost:5000/api"
        self.test_data = {}
        self.failure_scenarios = []
        self.notification_events = []
        
    def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive System Testing...")
        
        try:
            # 1. Database Tests
            self.test_database_operations()
            
            # 2. Data Flow Tests
            self.test_data_flow_integration()
            
            # 3. Failure Event Tests
            self.test_failure_scenarios()
            
            # 4. Notification Tests
            self.test_notification_system()
            
            # 5. Performance Tests
            self.test_performance_under_load()
            
            # 6. Security Tests
            self.test_security_vulnerabilities()
            
            # 7. Integration Tests
            self.test_system_integration()
            
            # 8. Edge Case Tests
            self.test_edge_cases()
            
            # Generate comprehensive report
            self.generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ Critical test failure: {str(e)}")
            raise
    
    def test_database_operations(self):
        """Test database operations comprehensively"""
        logger.info("📊 Testing Database Operations...")
        
        test_cases = [
            {
                'name': 'Create Customer Record',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': 'Test Customer',
                    'email': 'test@example.com',
                    'phone': '+1234567890',
                    'address': '123 Test St',
                    'city': 'Test City',
                    'state': 'TS',
                    'zip_code': '12345',
                    'country': 'Test Country'
                },
                'expected_status': 201
            },
            {
                'name': 'Create Product Record',
                'endpoint': '/supply_chain/items',
                'method': 'POST',
                'data': {
                    'name': 'Test Product',
                    'description': 'Test Product Description',
                    'sku': 'TEST-001',
                    'price': 99.99,
                    'category': 'Test Category',
                    'stock_quantity': 100
                },
                'expected_status': 201
            },
            {
                'name': 'Create Employee Record',
                'endpoint': '/people/employees',
                'method': 'POST',
                'data': {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'email': 'john.doe@company.com',
                    'phone': '+1234567890',
                    'department': 'Engineering',
                    'position': 'Software Engineer',
                    'hire_date': '2024-01-01',
                    'salary': 75000
                },
                'expected_status': 201
            },
            {
                'name': 'Create Invoice Record',
                'endpoint': '/finance/invoices',
                'method': 'POST',
                'data': {
                    'customer_id': 1,
                    'invoice_number': 'INV-001',
                    'amount': 1500.00,
                    'due_date': '2024-02-01',
                    'status': 'pending',
                    'items': [
                        {
                            'description': 'Test Item',
                            'quantity': 2,
                            'unit_price': 750.00,
                            'total': 1500.00
                        }
                    ]
                },
                'expected_status': 201
            }
        ]
        
        for test_case in test_cases:
            try:
                result = self._make_api_request(
                    test_case['method'],
                    test_case['endpoint'],
                    test_case['data']
                )
                
                if result['status_code'] == test_case['expected_status']:
                    self.test_results['database_tests'].append({
                        'test': test_case['name'],
                        'status': 'PASS',
                        'response_time': result['response_time'],
                        'data_created': result.get('data', {}).get('id')
                    })
                    logger.info(f"✅ {test_case['name']} - PASSED")
                else:
                    self.test_results['database_tests'].append({
                        'test': test_case['name'],
                        'status': 'FAIL',
                        'error': f"Expected {test_case['expected_status']}, got {result['status_code']}",
                        'response': result.get('response')
                    })
                    logger.error(f"❌ {test_case['name']} - FAILED")
                    
            except Exception as e:
                self.test_results['database_tests'].append({
                    'test': test_case['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"💥 {test_case['name']} - ERROR: {str(e)}")
    
    def test_data_flow_integration(self):
        """Test data flow between modules"""
        logger.info("🔄 Testing Data Flow Integration...")
        
        # Test CRM to Finance flow
        try:
            # 1. Create customer
            customer_result = self._make_api_request('POST', '/crm/customers', {
                'name': 'Flow Test Customer',
                'email': 'flow@example.com',
                'phone': '+1234567890'
            })
            
            if customer_result['status_code'] == 201:
                customer_id = customer_result['data']['id']
                
                # 2. Create opportunity
                opportunity_result = self._make_api_request('POST', '/crm/opportunities', {
                    'customer_id': customer_id,
                    'title': 'Flow Test Opportunity',
                    'amount': 5000.00,
                    'stage': 'proposal',
                    'probability': 75
                })
                
                if opportunity_result['status_code'] == 201:
                    opportunity_id = opportunity_result['data']['id']
                    
                    # 3. Create quote
                    quote_result = self._make_api_request('POST', '/crm/quotes', {
                        'customer_id': customer_id,
                        'opportunity_id': opportunity_id,
                        'quote_number': 'QTE-001',
                        'amount': 5000.00,
                        'valid_until': '2024-02-01'
                    })
                    
                    if quote_result['status_code'] == 201:
                        self.test_results['data_flow_tests'].append({
                            'test': 'CRM to Finance Flow',
                            'status': 'PASS',
                            'customer_id': customer_id,
                            'opportunity_id': opportunity_id,
                            'quote_id': quote_result['data']['id']
                        })
                        logger.info("✅ CRM to Finance Flow - PASSED")
                    else:
                        self.test_results['data_flow_tests'].append({
                            'test': 'CRM to Finance Flow',
                            'status': 'FAIL',
                            'error': f"Quote creation failed: {quote_result['status_code']}"
                        })
                        logger.error("❌ CRM to Finance Flow - FAILED")
                else:
                    self.test_results['data_flow_tests'].append({
                        'test': 'CRM to Finance Flow',
                        'status': 'FAIL',
                        'error': f"Opportunity creation failed: {opportunity_result['status_code']}"
                    })
                    logger.error("❌ CRM to Finance Flow - FAILED")
            else:
                self.test_results['data_flow_tests'].append({
                    'test': 'CRM to Finance Flow',
                    'status': 'FAIL',
                    'error': f"Customer creation failed: {customer_result['status_code']}"
                })
                logger.error("❌ CRM to Finance Flow - FAILED")
                
        except Exception as e:
            self.test_results['data_flow_tests'].append({
                'test': 'CRM to Finance Flow',
                'status': 'ERROR',
                'error': str(e)
            })
            logger.error(f"💥 CRM to Finance Flow - ERROR: {str(e)}")
    
    def test_failure_scenarios(self):
        """Test system behavior under failure conditions"""
        logger.info("💥 Testing Failure Scenarios...")
        
        failure_tests = [
            {
                'name': 'Invalid Data Format',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': '',  # Empty name
                    'email': 'invalid-email',  # Invalid email
                    'phone': 'invalid-phone'  # Invalid phone
                },
                'expected_status': 400
            },
            {
                'name': 'Missing Required Fields',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': 'Test Customer'
                    # Missing required fields
                },
                'expected_status': 400
            },
            {
                'name': 'Duplicate Email',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': 'Duplicate Test',
                    'email': 'duplicate@example.com',
                    'phone': '+1234567890'
                },
                'expected_status': 409  # Conflict
            },
            {
                'name': 'Invalid ID Reference',
                'endpoint': '/finance/invoices',
                'method': 'POST',
                'data': {
                    'customer_id': 99999,  # Non-existent customer
                    'invoice_number': 'INV-002',
                    'amount': 1000.00
                },
                'expected_status': 400
            },
            {
                'name': 'SQL Injection Attempt',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': "'; DROP TABLE customers; --",
                    'email': 'injection@example.com',
                    'phone': '+1234567890'
                },
                'expected_status': 400
            },
            {
                'name': 'XSS Attack Attempt',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': '<script>alert("XSS")</script>',
                    'email': 'xss@example.com',
                    'phone': '+1234567890'
                },
                'expected_status': 400
            }
        ]
        
        for test_case in failure_tests:
            try:
                result = self._make_api_request(
                    test_case['method'],
                    test_case['endpoint'],
                    test_case['data']
                )
                
                if result['status_code'] == test_case['expected_status']:
                    self.test_results['failure_tests'].append({
                        'test': test_case['name'],
                        'status': 'PASS',
                        'response_time': result['response_time'],
                        'security_blocked': True
                    })
                    logger.info(f"✅ {test_case['name']} - PASSED (Security Working)")
                else:
                    self.test_results['failure_tests'].append({
                        'test': test_case['name'],
                        'status': 'FAIL',
                        'error': f"Expected {test_case['expected_status']}, got {result['status_code']}",
                        'security_concern': True
                    })
                    logger.error(f"❌ {test_case['name']} - FAILED (Security Issue)")
                    
            except Exception as e:
                self.test_results['failure_tests'].append({
                    'test': test_case['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"💥 {test_case['name']} - ERROR: {str(e)}")
    
    def test_notification_system(self):
        """Test notification system comprehensively"""
        logger.info("🔔 Testing Notification System...")
        
        notification_tests = [
            {
                'name': 'Email Notification',
                'type': 'email',
                'recipient': 'test@example.com',
                'subject': 'Test Notification',
                'body': 'This is a test notification',
                'priority': 'normal'
            },
            {
                'name': 'SMS Notification',
                'type': 'sms',
                'recipient': '+1234567890',
                'message': 'Test SMS notification',
                'priority': 'high'
            },
            {
                'name': 'Push Notification',
                'type': 'push',
                'recipient': 'user123',
                'title': 'Test Push',
                'body': 'Test push notification',
                'priority': 'normal'
            },
            {
                'name': 'Webhook Notification',
                'type': 'webhook',
                'url': 'https://webhook.site/test',
                'event': 'data_created',
                'data': {'test': 'data'}
            }
        ]
        
        for test_case in notification_tests:
            try:
                result = self._make_api_request('POST', '/notifications/send', test_case)
                
                if result['status_code'] == 200:
                    self.test_results['notification_tests'].append({
                        'test': test_case['name'],
                        'status': 'PASS',
                        'notification_id': result['data'].get('id'),
                        'delivery_status': result['data'].get('status')
                    })
                    logger.info(f"✅ {test_case['name']} - PASSED")
                else:
                    self.test_results['notification_tests'].append({
                        'test': test_case['name'],
                        'status': 'FAIL',
                        'error': f"Notification failed: {result['status_code']}"
                    })
                    logger.error(f"❌ {test_case['name']} - FAILED")
                    
            except Exception as e:
                self.test_results['notification_tests'].append({
                    'test': test_case['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"💥 {test_case['name']} - ERROR: {str(e)}")
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        logger.info("⚡ Testing Performance Under Load...")
        
        # Test concurrent requests
        def make_concurrent_request(request_id):
            try:
                start_time = time.time()
                result = self._make_api_request('GET', '/crm/customers', {})
                end_time = time.time()
                
                return {
                    'request_id': request_id,
                    'response_time': end_time - start_time,
                    'status_code': result['status_code'],
                    'success': result['status_code'] == 200
                }
            except Exception as e:
                return {
                    'request_id': request_id,
                    'error': str(e),
                    'success': False
                }
        
        # Run 100 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(100)]
            results = [future.result() for future in futures]
        
        # Analyze results
        successful_requests = [r for r in results if r.get('success', False)]
        failed_requests = [r for r in results if not r.get('success', False)]
        
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
            min_response_time = min(r['response_time'] for r in successful_requests)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        self.test_results['performance_tests'].append({
            'test': 'Concurrent Load Test',
            'total_requests': 100,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / 100 * 100,
            'avg_response_time': avg_response_time,
            'max_response_time': max_response_time,
            'min_response_time': min_response_time,
            'status': 'PASS' if len(successful_requests) >= 95 else 'FAIL'
        })
        
        logger.info(f"✅ Load Test - {len(successful_requests)}/100 successful ({len(successful_requests)/100*100:.1f}%)")
        logger.info(f"📊 Avg Response Time: {avg_response_time:.3f}s")
        logger.info(f"📊 Max Response Time: {max_response_time:.3f}s")
    
    def test_security_vulnerabilities(self):
        """Test for security vulnerabilities"""
        logger.info("🔒 Testing Security Vulnerabilities...")
        
        security_tests = [
            {
                'name': 'Authentication Bypass',
                'endpoint': '/crm/customers',
                'method': 'GET',
                'headers': {},  # No authentication
                'expected_status': 401
            },
            {
                'name': 'SQL Injection',
                'endpoint': '/crm/customers',
                'method': 'GET',
                'params': {'search': "'; DROP TABLE customers; --"},
                'expected_status': 400
            },
            {
                'name': 'XSS Attack',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': '<script>alert("XSS")</script>',
                    'email': 'xss@example.com'
                },
                'expected_status': 400
            },
            {
                'name': 'CSRF Attack',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'headers': {'X-CSRF-Token': 'invalid'},
                'data': {'name': 'CSRF Test'},
                'expected_status': 403
            },
            {
                'name': 'Rate Limiting',
                'endpoint': '/crm/customers',
                'method': 'GET',
                'requests': 1000,  # Exceed rate limit
                'expected_status': 429
            }
        ]
        
        for test_case in security_tests:
            try:
                if test_case['name'] == 'Rate Limiting':
                    # Test rate limiting with multiple requests
                    for i in range(test_case['requests']):
                        result = self._make_api_request(
                            test_case['method'],
                            test_case['endpoint'],
                            {},
                            test_case.get('headers', {})
                        )
                        if result['status_code'] == 429:
                            break
                else:
                    result = self._make_api_request(
                        test_case['method'],
                        test_case['endpoint'],
                        test_case.get('data', {}),
                        test_case.get('headers', {})
                    )
                
                if result['status_code'] == test_case['expected_status']:
                    self.test_results['security_tests'].append({
                        'test': test_case['name'],
                        'status': 'PASS',
                        'security_blocked': True
                    })
                    logger.info(f"✅ {test_case['name']} - PASSED (Security Working)")
                else:
                    self.test_results['security_tests'].append({
                        'test': test_case['name'],
                        'status': 'FAIL',
                        'error': f"Expected {test_case['expected_status']}, got {result['status_code']}",
                        'security_concern': True
                    })
                    logger.error(f"❌ {test_case['name']} - FAILED (Security Issue)")
                    
            except Exception as e:
                self.test_results['security_tests'].append({
                    'test': test_case['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"💥 {test_case['name']} - ERROR: {str(e)}")
    
    def test_system_integration(self):
        """Test system integration between modules"""
        logger.info("🔗 Testing System Integration...")
        
        integration_tests = [
            {
                'name': 'CRM to Finance Integration',
                'steps': [
                    {'module': 'CRM', 'action': 'create_customer'},
                    {'module': 'CRM', 'action': 'create_opportunity'},
                    {'module': 'Finance', 'action': 'create_invoice'},
                    {'module': 'Finance', 'action': 'process_payment'}
                ]
            },
            {
                'name': 'Supply Chain to Finance Integration',
                'steps': [
                    {'module': 'Supply Chain', 'action': 'create_supplier'},
                    {'module': 'Supply Chain', 'action': 'create_purchase_order'},
                    {'module': 'Finance', 'action': 'create_bill'},
                    {'module': 'Finance', 'action': 'process_payment'}
                ]
            },
            {
                'name': 'People to Finance Integration',
                'steps': [
                    {'module': 'People', 'action': 'create_employee'},
                    {'module': 'People', 'action': 'create_payroll'},
                    {'module': 'Finance', 'action': 'process_payroll'},
                    {'module': 'Finance', 'action': 'generate_payroll_report'}
                ]
            }
        ]
        
        for test_case in integration_tests:
            try:
                integration_success = True
                step_results = []
                
                for step in test_case['steps']:
                    step_result = self._execute_integration_step(step)
                    step_results.append(step_result)
                    
                    if not step_result['success']:
                        integration_success = False
                        break
                
                self.test_results['integration_tests'].append({
                    'test': test_case['name'],
                    'status': 'PASS' if integration_success else 'FAIL',
                    'steps': step_results,
                    'integration_success': integration_success
                })
                
                if integration_success:
                    logger.info(f"✅ {test_case['name']} - PASSED")
                else:
                    logger.error(f"❌ {test_case['name']} - FAILED")
                    
            except Exception as e:
                self.test_results['integration_tests'].append({
                    'test': test_case['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"💥 {test_case['name']} - ERROR: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        logger.info("🎯 Testing Edge Cases...")
        
        edge_cases = [
            {
                'name': 'Maximum String Length',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': 'A' * 1000,  # Very long name
                    'email': 'test@example.com',
                    'phone': '+1234567890'
                },
                'expected_status': 400
            },
            {
                'name': 'Negative Numbers',
                'endpoint': '/finance/invoices',
                'method': 'POST',
                'data': {
                    'customer_id': 1,
                    'amount': -1000.00,  # Negative amount
                    'invoice_number': 'INV-003'
                },
                'expected_status': 400
            },
            {
                'name': 'Future Dates',
                'endpoint': '/people/employees',
                'method': 'POST',
                'data': {
                    'first_name': 'Future',
                    'last_name': 'Employee',
                    'email': 'future@example.com',
                    'hire_date': '2030-01-01'  # Future date
                },
                'expected_status': 400
            },
            {
                'name': 'Special Characters',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': 'Test Customer !@#$%^&*()',
                    'email': 'special@example.com',
                    'phone': '+1-234-567-8900'
                },
                'expected_status': 201
            },
            {
                'name': 'Unicode Characters',
                'endpoint': '/crm/customers',
                'method': 'POST',
                'data': {
                    'name': '测试客户 🚀',
                    'email': 'unicode@example.com',
                    'phone': '+1234567890'
                },
                'expected_status': 201
            }
        ]
        
        for test_case in edge_cases:
            try:
                result = self._make_api_request(
                    test_case['method'],
                    test_case['endpoint'],
                    test_case['data']
                )
                
                if result['status_code'] == test_case['expected_status']:
                    self.test_results['edge_case_tests'].append({
                        'test': test_case['name'],
                        'status': 'PASS',
                        'response_time': result['response_time']
                    })
                    logger.info(f"✅ {test_case['name']} - PASSED")
                else:
                    self.test_results['edge_case_tests'].append({
                        'test': test_case['name'],
                        'status': 'FAIL',
                        'error': f"Expected {test_case['expected_status']}, got {result['status_code']}"
                    })
                    logger.error(f"❌ {test_case['name']} - FAILED")
                    
            except Exception as e:
                self.test_results['edge_case_tests'].append({
                    'test': test_case['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
                logger.error(f"💥 {test_case['name']} - ERROR: {str(e)}")
    
    def _make_api_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict:
        """Make API request and return result"""
        try:
            url = f"{self.base_url}{endpoint}"
            request_headers = {
                'Content-Type': 'application/json',
                'X-User-ID': 'test-user',
                **(headers or {})
            }
            
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'response': response.json() if response.content else {},
                'data': response.json() if response.content else {}
            }
            
        except requests.exceptions.Timeout:
            return {
                'status_code': 408,
                'response_time': 30.0,
                'error': 'Request timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status_code': 503,
                'response_time': 0.0,
                'error': 'Connection error'
            }
        except Exception as e:
            return {
                'status_code': 500,
                'response_time': 0.0,
                'error': str(e)
            }
    
    def _execute_integration_step(self, step: Dict) -> Dict:
        """Execute a single integration step"""
        try:
            if step['action'] == 'create_customer':
                result = self._make_api_request('POST', '/crm/customers', {
                    'name': f"Integration Test Customer {random.randint(1000, 9999)}",
                    'email': f"integration{random.randint(1000, 9999)}@example.com",
                    'phone': '+1234567890'
                })
                return {'success': result['status_code'] == 201, 'step': step, 'result': result}
            
            elif step['action'] == 'create_opportunity':
                result = self._make_api_request('POST', '/crm/opportunities', {
                    'customer_id': 1,
                    'title': f"Integration Test Opportunity {random.randint(1000, 9999)}",
                    'amount': 5000.00,
                    'stage': 'proposal'
                })
                return {'success': result['status_code'] == 201, 'step': step, 'result': result}
            
            elif step['action'] == 'create_invoice':
                result = self._make_api_request('POST', '/finance/invoices', {
                    'customer_id': 1,
                    'invoice_number': f"INV-{random.randint(1000, 9999)}",
                    'amount': 1500.00,
                    'due_date': '2024-02-01'
                })
                return {'success': result['status_code'] == 201, 'step': step, 'result': result}
            
            else:
                return {'success': False, 'step': step, 'error': f"Unknown action: {step['action']}"}
                
        except Exception as e:
            return {'success': False, 'step': step, 'error': str(e)}
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating Comprehensive Test Report...")
        
        total_tests = sum(len(tests) for tests in self.test_results.values())
        passed_tests = sum(
            len([t for t in tests if t.get('status') == 'PASS'])
            for tests in self.test_results.values()
        )
        failed_tests = sum(
            len([t for t in tests if t.get('status') == 'FAIL'])
            for tests in self.test_results.values()
        )
        error_tests = sum(
            len([t for t in tests if t.get('status') == 'ERROR'])
            for tests in self.test_results.values()
        )
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'success_rate': success_rate
            },
            'detailed_results': self.test_results,
            'recommendations': self._generate_recommendations(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report to file
        with open('comprehensive_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Test Report Generated:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        logger.info(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        logger.info(f"   Errors: {error_tests} ({error_tests/total_tests*100:.1f}%)")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for security issues
        security_failures = [
            t for tests in self.test_results['security_tests']
            for t in tests if t.get('status') == 'FAIL'
        ]
        if security_failures:
            recommendations.append("🔒 Security vulnerabilities detected. Review and fix security issues immediately.")
        
        # Check for performance issues
        performance_tests = self.test_results['performance_tests']
        if performance_tests:
            for test in performance_tests:
                if test.get('success_rate', 0) < 95:
                    recommendations.append("⚡ Performance issues detected. Consider optimizing database queries and adding caching.")
        
        # Check for integration issues
        integration_failures = [
            t for tests in self.test_results['integration_tests']
            for t in tests if t.get('status') == 'FAIL'
        ]
        if integration_failures:
            recommendations.append("🔗 Integration issues detected. Review module communication and data flow.")
        
        # Check for notification issues
        notification_failures = [
            t for tests in self.test_results['notification_tests']
            for t in tests if t.get('status') == 'FAIL'
        ]
        if notification_failures:
            recommendations.append("🔔 Notification system issues detected. Review notification delivery mechanisms.")
        
        return recommendations

# Run comprehensive tests
if __name__ == "__main__":
    tester = ComprehensiveSystemTester()
    tester.run_all_tests()
