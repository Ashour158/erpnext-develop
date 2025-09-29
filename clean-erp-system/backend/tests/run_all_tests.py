#!/usr/bin/env python3
# Comprehensive Test Runner
# Runs all system tests and generates comprehensive reports

import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import test modules
from test_comprehensive_system import ComprehensiveSystemTester
from test_database_integrity import DatabaseIntegrityTester
from test_failure_scenarios import FailureScenarioTester
from test_notification_system import NotificationSystemTester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterTestRunner:
    """
    Master Test Runner
    Orchestrates all system tests and generates comprehensive reports
    """
    
    def __init__(self):
        self.test_results = {
            'comprehensive_system': {},
            'database_integrity': {},
            'failure_scenarios': {},
            'notification_system': {}
        }
        self.overall_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'success_rate': 0.0,
            'execution_time': 0.0,
            'start_time': None,
            'end_time': None
        }
        self.recommendations = []
        self.critical_issues = []
        
    def run_all_tests(self):
        """Run all system tests"""
        logger.info("🚀 Starting Master Test Execution...")
        start_time = time.time()
        self.overall_results['start_time'] = datetime.now().isoformat()
        
        try:
            # 1. Comprehensive System Tests
            logger.info("📊 Running Comprehensive System Tests...")
            comprehensive_tester = ComprehensiveSystemTester()
            comprehensive_tester.run_all_tests()
            self.test_results['comprehensive_system'] = comprehensive_tester.test_results
            
            # 2. Database Integrity Tests
            logger.info("🗄️ Running Database Integrity Tests...")
            database_tester = DatabaseIntegrityTester()
            database_tester.run_database_tests()
            self.test_results['database_integrity'] = database_tester.test_results
            
            # 3. Failure Scenario Tests
            logger.info("💥 Running Failure Scenario Tests...")
            failure_tester = FailureScenarioTester()
            failure_tester.run_failure_tests()
            self.test_results['failure_scenarios'] = failure_tester.test_results
            
            # 4. Notification System Tests
            logger.info("🔔 Running Notification System Tests...")
            notification_tester = NotificationSystemTester()
            notification_tester.run_notification_tests()
            self.test_results['notification_system'] = notification_tester.test_results
            
            # Calculate overall results
            self._calculate_overall_results()
            
            # Generate recommendations
            self._generate_recommendations()
            
            # Generate master report
            self._generate_master_report()
            
        except Exception as e:
            logger.error(f"❌ Critical error in master test execution: {str(e)}")
            self.critical_issues.append(f"Master test execution failed: {str(e)}")
            raise
        
        finally:
            end_time = time.time()
            self.overall_results['end_time'] = datetime.now().isoformat()
            self.overall_results['execution_time'] = end_time - start_time
            
            logger.info(f"🏁 Master Test Execution Completed in {self.overall_results['execution_time']:.2f} seconds")
    
    def _calculate_overall_results(self):
        """Calculate overall test results"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        error_tests = 0
        
        for test_suite, results in self.test_results.items():
            for test_category, tests in results.items():
                if isinstance(tests, list):
                    total_tests += len(tests)
                    passed_tests += len([t for t in tests if t.get('status') == 'PASS'])
                    failed_tests += len([t for t in tests if t.get('status') == 'FAIL'])
                    error_tests += len([t for t in tests if t.get('status') == 'ERROR'])
        
        self.overall_results.update({
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        })
    
    def _generate_recommendations(self):
        """Generate comprehensive recommendations"""
        self.recommendations = []
        
        # Check for critical issues
        if self.overall_results['success_rate'] < 80:
            self.recommendations.append("🚨 CRITICAL: Overall success rate is below 80%. Immediate attention required.")
            self.critical_issues.append("Low overall success rate")
        
        # Check for database issues
        db_failures = self._count_failures('database_integrity')
        if db_failures > 0:
            self.recommendations.append(f"🗄️ Database integrity issues detected ({db_failures} failures). Review database operations and constraints.")
        
        # Check for failure handling issues
        failure_failures = self._count_failures('failure_scenarios')
        if failure_failures > 0:
            self.recommendations.append(f"💥 Failure handling issues detected ({failure_failures} failures). Review error handling and recovery mechanisms.")
        
        # Check for notification issues
        notification_failures = self._count_failures('notification_system')
        if notification_failures > 0:
            self.recommendations.append(f"🔔 Notification system issues detected ({notification_failures} failures). Review notification delivery and reliability.")
        
        # Check for performance issues
        performance_issues = self._check_performance_issues()
        if performance_issues:
            self.recommendations.append(f"⚡ Performance issues detected. Review system performance and optimization.")
        
        # Check for security issues
        security_issues = self._check_security_issues()
        if security_issues:
            self.recommendations.append(f"🔒 Security issues detected. Review security measures and vulnerability handling.")
        
        # Check for integration issues
        integration_issues = self._check_integration_issues()
        if integration_issues:
            self.recommendations.append(f"🔗 Integration issues detected. Review system integration and communication.")
    
    def _count_failures(self, test_suite: str) -> int:
        """Count failures in a specific test suite"""
        failures = 0
        if test_suite in self.test_results:
            for test_category, tests in self.test_results[test_suite].items():
                if isinstance(tests, list):
                    failures += len([t for t in tests if t.get('status') == 'FAIL'])
        return failures
    
    def _check_performance_issues(self) -> bool:
        """Check for performance issues"""
        # Check comprehensive system performance
        if 'comprehensive_system' in self.test_results:
            performance_tests = self.test_results['comprehensive_system'].get('performance_tests', [])
            for test in performance_tests:
                if test.get('success_rate', 0) < 95:
                    return True
        
        # Check notification performance
        if 'notification_system' in self.test_results:
            notification_tests = self.test_results['notification_system'].get('notification_performance', [])
            for test in notification_tests:
                if test.get('success_rate', 0) < 95:
                    return True
        
        return False
    
    def _check_security_issues(self) -> bool:
        """Check for security issues"""
        # Check comprehensive system security
        if 'comprehensive_system' in self.test_results:
            security_tests = self.test_results['comprehensive_system'].get('security_tests', [])
            for test in security_tests:
                if test.get('status') == 'FAIL':
                    return True
        
        # Check failure scenario security
        if 'failure_scenarios' in self.test_results:
            security_tests = self.test_results['failure_scenarios'].get('security_failures', [])
            for test in security_tests:
                if test.get('status') == 'FAIL':
                    return True
        
        return False
    
    def _check_integration_issues(self) -> bool:
        """Check for integration issues"""
        # Check comprehensive system integration
        if 'comprehensive_system' in self.test_results:
            integration_tests = self.test_results['comprehensive_system'].get('integration_tests', [])
            for test in integration_tests:
                if test.get('status') == 'FAIL':
                    return True
        
        return False
    
    def _generate_master_report(self):
        """Generate comprehensive master report"""
        logger.info("📊 Generating Master Test Report...")
        
        report = {
            'test_execution_summary': {
                'execution_time': self.overall_results['execution_time'],
                'start_time': self.overall_results['start_time'],
                'end_time': self.overall_results['end_time'],
                'total_tests': self.overall_results['total_tests'],
                'passed_tests': self.overall_results['passed_tests'],
                'failed_tests': self.overall_results['failed_tests'],
                'error_tests': self.overall_results['error_tests'],
                'success_rate': self.overall_results['success_rate']
            },
            'test_suite_results': {
                'comprehensive_system': {
                    'total_tests': self._count_tests('comprehensive_system'),
                    'passed_tests': self._count_passed('comprehensive_system'),
                    'failed_tests': self._count_failures('comprehensive_system'),
                    'error_tests': self._count_errors('comprehensive_system'),
                    'success_rate': self._calculate_success_rate('comprehensive_system')
                },
                'database_integrity': {
                    'total_tests': self._count_tests('database_integrity'),
                    'passed_tests': self._count_passed('database_integrity'),
                    'failed_tests': self._count_failures('database_integrity'),
                    'error_tests': self._count_errors('database_integrity'),
                    'success_rate': self._calculate_success_rate('database_integrity')
                },
                'failure_scenarios': {
                    'total_tests': self._count_tests('failure_scenarios'),
                    'passed_tests': self._count_passed('failure_scenarios'),
                    'failed_tests': self._count_failures('failure_scenarios'),
                    'error_tests': self._count_errors('failure_scenarios'),
                    'success_rate': self._calculate_success_rate('failure_scenarios')
                },
                'notification_system': {
                    'total_tests': self._count_tests('notification_system'),
                    'passed_tests': self._count_passed('notification_system'),
                    'failed_tests': self._count_failures('notification_system'),
                    'error_tests': self._count_errors('notification_system'),
                    'success_rate': self._calculate_success_rate('notification_system')
                }
            },
            'detailed_results': self.test_results,
            'recommendations': self.recommendations,
            'critical_issues': self.critical_issues,
            'system_health': self._assess_system_health(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save master report
        with open('master_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate summary report
        self._generate_summary_report()
        
        logger.info(f"📊 Master Test Report Generated:")
        logger.info(f"   Total Tests: {self.overall_results['total_tests']}")
        logger.info(f"   Passed: {self.overall_results['passed_tests']} ({self.overall_results['passed_tests']/self.overall_results['total_tests']*100:.1f}%)")
        logger.info(f"   Failed: {self.overall_results['failed_tests']} ({self.overall_results['failed_tests']/self.overall_results['total_tests']*100:.1f}%)")
        logger.info(f"   Errors: {self.overall_results['error_tests']} ({self.overall_results['error_tests']/self.overall_results['total_tests']*100:.1f}%)")
        logger.info(f"   Success Rate: {self.overall_results['success_rate']:.1f}%")
        logger.info(f"   Execution Time: {self.overall_results['execution_time']:.2f} seconds")
        
        return report
    
    def _count_tests(self, test_suite: str) -> int:
        """Count total tests in a test suite"""
        total = 0
        if test_suite in self.test_results:
            for test_category, tests in self.test_results[test_suite].items():
                if isinstance(tests, list):
                    total += len(tests)
        return total
    
    def _count_passed(self, test_suite: str) -> int:
        """Count passed tests in a test suite"""
        passed = 0
        if test_suite in self.test_results:
            for test_category, tests in self.test_results[test_suite].items():
                if isinstance(tests, list):
                    passed += len([t for t in tests if t.get('status') == 'PASS'])
        return passed
    
    def _count_failures(self, test_suite: str) -> int:
        """Count failures in a test suite"""
        failures = 0
        if test_suite in self.test_results:
            for test_category, tests in self.test_results[test_suite].items():
                if isinstance(tests, list):
                    failures += len([t for t in tests if t.get('status') == 'FAIL'])
        return failures
    
    def _count_errors(self, test_suite: str) -> int:
        """Count errors in a test suite"""
        errors = 0
        if test_suite in self.test_results:
            for test_category, tests in self.test_results[test_suite].items():
                if isinstance(tests, list):
                    errors += len([t for t in tests if t.get('status') == 'ERROR'])
        return errors
    
    def _calculate_success_rate(self, test_suite: str) -> float:
        """Calculate success rate for a test suite"""
        total = self._count_tests(test_suite)
        passed = self._count_passed(test_suite)
        return (passed / total * 100) if total > 0 else 0
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        health_score = self.overall_results['success_rate']
        
        if health_score >= 95:
            health_status = 'EXCELLENT'
            health_color = 'green'
        elif health_score >= 85:
            health_status = 'GOOD'
            health_color = 'yellow'
        elif health_score >= 70:
            health_status = 'FAIR'
            health_color = 'orange'
        else:
            health_status = 'POOR'
            health_color = 'red'
        
        return {
            'health_score': health_score,
            'health_status': health_status,
            'health_color': health_color,
            'critical_issues_count': len(self.critical_issues),
            'recommendations_count': len(self.recommendations)
        }
    
    def _generate_summary_report(self):
        """Generate human-readable summary report"""
        summary = f"""
# 🧪 COMPREHENSIVE SYSTEM TEST REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 EXECUTION SUMMARY
- **Total Tests**: {self.overall_results['total_tests']}
- **Passed**: {self.overall_results['passed_tests']} ({self.overall_results['passed_tests']/self.overall_results['total_tests']*100:.1f}%)
- **Failed**: {self.overall_results['failed_tests']} ({self.overall_results['failed_tests']/self.overall_results['total_tests']*100:.1f}%)
- **Errors**: {self.overall_results['error_tests']} ({self.overall_results['error_tests']/self.overall_results['total_tests']*100:.1f}%)
- **Success Rate**: {self.overall_results['success_rate']:.1f}%
- **Execution Time**: {self.overall_results['execution_time']:.2f} seconds

## 🏥 SYSTEM HEALTH
- **Health Score**: {self._assess_system_health()['health_score']:.1f}%
- **Health Status**: {self._assess_system_health()['health_status']}
- **Critical Issues**: {len(self.critical_issues)}
- **Recommendations**: {len(self.recommendations)}

## 📋 TEST SUITE RESULTS
"""
        
        for test_suite in ['comprehensive_system', 'database_integrity', 'failure_scenarios', 'notification_system']:
            total = self._count_tests(test_suite)
            passed = self._count_passed(test_suite)
            failed = self._count_failures(test_suite)
            errors = self._count_errors(test_suite)
            success_rate = self._calculate_success_rate(test_suite)
            
            summary += f"""
### {test_suite.replace('_', ' ').title()}
- **Total Tests**: {total}
- **Passed**: {passed} ({passed/total*100:.1f}%)
- **Failed**: {failed} ({failed/total*100:.1f}%)
- **Errors**: {errors} ({errors/total*100:.1f}%)
- **Success Rate**: {success_rate:.1f}%
"""
        
        if self.recommendations:
            summary += "\n## 🎯 RECOMMENDATIONS\n"
            for i, rec in enumerate(self.recommendations, 1):
                summary += f"{i}. {rec}\n"
        
        if self.critical_issues:
            summary += "\n## 🚨 CRITICAL ISSUES\n"
            for i, issue in enumerate(self.critical_issues, 1):
                summary += f"{i}. {issue}\n"
        
        # Save summary report
        with open('test_summary_report.md', 'w') as f:
            f.write(summary)
        
        logger.info("📄 Summary report generated: test_summary_report.md")

def main():
    """Main execution function"""
    try:
        runner = MasterTestRunner()
        runner.run_all_tests()
        
        # Print final results
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE SYSTEM TESTING COMPLETED!")
        print("="*80)
        print(f"📊 Total Tests: {runner.overall_results['total_tests']}")
        print(f"✅ Passed: {runner.overall_results['passed_tests']}")
        print(f"❌ Failed: {runner.overall_results['failed_tests']}")
        print(f"💥 Errors: {runner.overall_results['error_tests']}")
        print(f"📈 Success Rate: {runner.overall_results['success_rate']:.1f}%")
        print(f"⏱️ Execution Time: {runner.overall_results['execution_time']:.2f} seconds")
        print(f"🏥 System Health: {runner._assess_system_health()['health_status']}")
        print("="*80)
        
        if runner.critical_issues:
            print("\n🚨 CRITICAL ISSUES DETECTED:")
            for issue in runner.critical_issues:
                print(f"   • {issue}")
        
        if runner.recommendations:
            print("\n🎯 RECOMMENDATIONS:")
            for rec in runner.recommendations:
                print(f"   • {rec}")
        
        print(f"\n📄 Reports generated:")
        print(f"   • master_test_report.json - Detailed JSON report")
        print(f"   • test_summary_report.md - Human-readable summary")
        print(f"   • test_execution.log - Execution log")
        
        return 0 if runner.overall_results['success_rate'] >= 80 else 1
        
    except Exception as e:
        logger.error(f"❌ Master test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
