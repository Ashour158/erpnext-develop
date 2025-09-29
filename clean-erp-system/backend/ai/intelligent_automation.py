# Intelligent Automation Engine
# AI-powered workflow automation and process optimization

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomationTrigger(Enum):
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"
    MANUAL = "manual"
    API_CALL = "api_call"

class AutomationStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ActionType(Enum):
    EMAIL = "email"
    NOTIFICATION = "notification"
    DATA_UPDATE = "data_update"
    API_CALL = "api_call"
    WORKFLOW_TRIGGER = "workflow_trigger"
    REPORT_GENERATION = "report_generation"
    APPROVAL_REQUEST = "approval_request"
    CUSTOM_SCRIPT = "custom_script"

@dataclass
class AutomationRule:
    id: str
    name: str
    description: str
    trigger: AutomationTrigger
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    status: AutomationStatus
    created_at: datetime
    updated_at: datetime
    created_by: str
    priority: int = 1
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_executed: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutomationExecution:
    id: str
    rule_id: str
    status: AutomationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    execution_data: Dict[str, Any] = field(default_factory=dict)
    results: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ProcessInsight:
    process_id: str
    process_name: str
    efficiency_score: float
    bottleneck_steps: List[str]
    optimization_suggestions: List[str]
    time_savings_potential: float
    cost_savings_potential: float
    confidence: float
    timestamp: datetime

class IntelligentAutomationEngine:
    """
    Advanced Intelligent Automation Engine for ERP System
    Provides AI-powered workflow automation, process optimization, and smart recommendations
    """
    
    def __init__(self):
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.execution_history: List[AutomationExecution] = []
        self.process_insights: List[ProcessInsight] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.condition_evaluators = {
            'equals': self._evaluate_equals,
            'not_equals': self._evaluate_not_equals,
            'greater_than': self._evaluate_greater_than,
            'less_than': self._evaluate_less_than,
            'contains': self._evaluate_contains,
            'not_contains': self._evaluate_not_contains,
            'is_empty': self._evaluate_is_empty,
            'is_not_empty': self._evaluate_is_not_empty,
            'date_range': self._evaluate_date_range,
            'custom': self._evaluate_custom
        }
        self.action_executors = {
            'email': self._execute_email_action,
            'notification': self._execute_notification_action,
            'data_update': self._execute_data_update_action,
            'api_call': self._execute_api_call_action,
            'workflow_trigger': self._execute_workflow_trigger_action,
            'report_generation': self._execute_report_generation_action,
            'approval_request': self._execute_approval_request_action,
            'custom_script': self._execute_custom_script_action
        }
    
    def create_automation_rule(self, 
                             name: str,
                             description: str,
                             trigger: AutomationTrigger,
                             conditions: List[Dict[str, Any]],
                             actions: List[Dict[str, Any]],
                             created_by: str,
                             priority: int = 1,
                             metadata: Optional[Dict[str, Any]] = None) -> AutomationRule:
        """
        Create a new automation rule
        """
        try:
            rule_id = str(uuid.uuid4())
            rule = AutomationRule(
                id=rule_id,
                name=name,
                description=description,
                trigger=trigger,
                conditions=conditions,
                actions=actions,
                status=AutomationStatus.ACTIVE,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=created_by,
                priority=priority,
                metadata=metadata or {}
            )
            
            self.automation_rules[rule_id] = rule
            logger.info(f"Created automation rule: {name} (ID: {rule_id})")
            return rule
            
        except Exception as e:
            logger.error(f"Error creating automation rule: {str(e)}")
            raise
    
    def update_automation_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing automation rule
        """
        try:
            if rule_id not in self.automation_rules:
                raise ValueError(f"Automation rule {rule_id} not found")
            
            rule = self.automation_rules[rule_id]
            
            # Update allowed fields
            allowed_fields = ['name', 'description', 'conditions', 'actions', 'status', 'priority', 'metadata']
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(rule, field, value)
            
            rule.updated_at = datetime.now()
            self.automation_rules[rule_id] = rule
            
            logger.info(f"Updated automation rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating automation rule: {str(e)}")
            return False
    
    def delete_automation_rule(self, rule_id: str) -> bool:
        """
        Delete an automation rule
        """
        try:
            if rule_id not in self.automation_rules:
                raise ValueError(f"Automation rule {rule_id} not found")
            
            del self.automation_rules[rule_id]
            logger.info(f"Deleted automation rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting automation rule: {str(e)}")
            return False
    
    def execute_automation_rule(self, rule_id: str, context_data: Dict[str, Any]) -> AutomationExecution:
        """
        Execute an automation rule
        """
        try:
            if rule_id not in self.automation_rules:
                raise ValueError(f"Automation rule {rule_id} not found")
            
            rule = self.automation_rules[rule_id]
            
            # Create execution record
            execution_id = str(uuid.uuid4())
            execution = AutomationExecution(
                id=execution_id,
                rule_id=rule_id,
                status=AutomationStatus.RUNNING,
                started_at=datetime.now(),
                execution_data=context_data
            )
            
            # Check if conditions are met
            conditions_met = self._evaluate_conditions(rule.conditions, context_data)
            
            if not conditions_met:
                execution.status = AutomationStatus.COMPLETED
                execution.completed_at = datetime.now()
                execution.results.append({"message": "Conditions not met, execution skipped"})
                self.execution_history.append(execution)
                return execution
            
            # Execute actions
            results = []
            for action in rule.actions:
                try:
                    result = self._execute_action(action, context_data)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error executing action {action}: {str(e)}")
                    results.append({"error": str(e), "action": action})
            
            # Update execution record
            execution.status = AutomationStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.results = results
            
            # Update rule statistics
            rule.execution_count += 1
            rule.success_count += 1
            rule.last_executed = datetime.now()
            
            self.execution_history.append(execution)
            self.automation_rules[rule_id] = rule
            
            logger.info(f"Executed automation rule: {rule.name} (Execution ID: {execution_id})")
            return execution
            
        except Exception as e:
            logger.error(f"Error executing automation rule: {str(e)}")
            execution.status = AutomationStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            self.execution_history.append(execution)
            return execution
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], context_data: Dict[str, Any]) -> bool:
        """
        Evaluate automation rule conditions
        """
        try:
            for condition in conditions:
                operator = condition.get('operator', 'equals')
                field = condition.get('field')
                value = condition.get('value')
                
                if field not in context_data:
                    return False
                
                context_value = context_data[field]
                
                if operator not in self.condition_evaluators:
                    logger.warning(f"Unknown condition operator: {operator}")
                    return False
                
                if not self.condition_evaluators[operator](context_value, value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating conditions: {str(e)}")
            return False
    
    def _evaluate_equals(self, context_value: Any, expected_value: Any) -> bool:
        return context_value == expected_value
    
    def _evaluate_not_equals(self, context_value: Any, expected_value: Any) -> bool:
        return context_value != expected_value
    
    def _evaluate_greater_than(self, context_value: Any, expected_value: Any) -> bool:
        try:
            return float(context_value) > float(expected_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_less_than(self, context_value: Any, expected_value: Any) -> bool:
        try:
            return float(context_value) < float(expected_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_contains(self, context_value: Any, expected_value: Any) -> bool:
        return str(expected_value).lower() in str(context_value).lower()
    
    def _evaluate_not_contains(self, context_value: Any, expected_value: Any) -> bool:
        return str(expected_value).lower() not in str(context_value).lower()
    
    def _evaluate_is_empty(self, context_value: Any, expected_value: Any) -> bool:
        return context_value is None or str(context_value).strip() == ""
    
    def _evaluate_is_not_empty(self, context_value: Any, expected_value: Any) -> bool:
        return context_value is not None and str(context_value).strip() != ""
    
    def _evaluate_date_range(self, context_value: Any, expected_value: Any) -> bool:
        try:
            if isinstance(context_value, str):
                context_date = datetime.fromisoformat(context_value)
            else:
                context_date = context_value
            
            start_date = datetime.fromisoformat(expected_value.get('start_date'))
            end_date = datetime.fromisoformat(expected_value.get('end_date'))
            
            return start_date <= context_date <= end_date
        except (ValueError, TypeError):
            return False
    
    def _evaluate_custom(self, context_value: Any, expected_value: Any) -> bool:
        # Custom condition evaluation logic
        # This would be implemented based on specific business requirements
        return True
    
    def _execute_action(self, action: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single automation action
        """
        try:
            action_type = action.get('type')
            action_config = action.get('config', {})
            
            if action_type not in self.action_executors:
                raise ValueError(f"Unknown action type: {action_type}")
            
            result = self.action_executors[action_type](action_config, context_data)
            return {
                'action_type': action_type,
                'status': 'success',
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing action: {str(e)}")
            return {
                'action_type': action.get('type', 'unknown'),
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _execute_email_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email action"""
        # Email sending logic would be implemented here
        return {"message": "Email sent successfully", "recipients": config.get('recipients', [])}
    
    def _execute_notification_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification action"""
        # Notification sending logic would be implemented here
        return {"message": "Notification sent successfully", "channels": config.get('channels', [])}
    
    def _execute_data_update_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data update action"""
        # Data update logic would be implemented here
        return {"message": "Data updated successfully", "updated_fields": config.get('fields', [])}
    
    def _execute_api_call_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call action"""
        # API call logic would be implemented here
        return {"message": "API call executed successfully", "endpoint": config.get('endpoint', '')}
    
    def _execute_workflow_trigger_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow trigger action"""
        # Workflow trigger logic would be implemented here
        return {"message": "Workflow triggered successfully", "workflow_id": config.get('workflow_id', '')}
    
    def _execute_report_generation_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation action"""
        # Report generation logic would be implemented here
        return {"message": "Report generated successfully", "report_type": config.get('report_type', '')}
    
    def _execute_approval_request_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute approval request action"""
        # Approval request logic would be implemented here
        return {"message": "Approval request sent successfully", "approvers": config.get('approvers', [])}
    
    def _execute_custom_script_action(self, config: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom script action"""
        # Custom script execution logic would be implemented here
        return {"message": "Custom script executed successfully", "script_id": config.get('script_id', '')}
    
    def analyze_process_efficiency(self, process_data: Dict[str, Any]) -> ProcessInsight:
        """
        Analyze process efficiency and provide optimization suggestions
        """
        try:
            process_id = process_data.get('process_id', str(uuid.uuid4()))
            process_name = process_data.get('process_name', 'Unknown Process')
            
            # Analyze process steps
            steps = process_data.get('steps', [])
            total_time = sum(step.get('duration', 0) for step in steps)
            avg_step_time = total_time / len(steps) if steps else 0
            
            # Identify bottlenecks (steps taking more than 2x average time)
            bottleneck_steps = [
                step['name'] for step in steps 
                if step.get('duration', 0) > avg_step_time * 2
            ]
            
            # Calculate efficiency score (0-100)
            efficiency_score = max(0, 100 - (len(bottleneck_steps) / len(steps) * 100)) if steps else 0
            
            # Generate optimization suggestions
            optimization_suggestions = []
            if bottleneck_steps:
                optimization_suggestions.append(f"Optimize {', '.join(bottleneck_steps)} steps")
            if avg_step_time > 60:  # More than 1 minute average
                optimization_suggestions.append("Consider parallel processing for long-running steps")
            if len(steps) > 10:
                optimization_suggestions.append("Consider breaking down the process into smaller sub-processes")
            
            # Calculate potential savings
            time_savings_potential = sum(
                step.get('duration', 0) - avg_step_time 
                for step in steps 
                if step.get('duration', 0) > avg_step_time * 1.5
            )
            
            cost_savings_potential = time_savings_potential * 0.5  # Assume $0.5 per minute saved
            
            insight = ProcessInsight(
                process_id=process_id,
                process_name=process_name,
                efficiency_score=efficiency_score,
                bottleneck_steps=bottleneck_steps,
                optimization_suggestions=optimization_suggestions,
                time_savings_potential=time_savings_potential,
                cost_savings_potential=cost_savings_potential,
                confidence=0.85,
                timestamp=datetime.now()
            )
            
            self.process_insights.append(insight)
            logger.info(f"Generated process insight for {process_name}: {efficiency_score:.1f}% efficiency")
            return insight
            
        except Exception as e:
            logger.error(f"Error analyzing process efficiency: {str(e)}")
            raise
    
    def get_automation_recommendations(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get AI-powered automation recommendations
        """
        try:
            recommendations = []
            
            # Analyze data patterns to suggest automations
            if 'sales_data' in context_data:
                sales_data = context_data['sales_data']
                if len(sales_data) > 100:  # Sufficient data for analysis
                    recommendations.append({
                        'type': 'sales_automation',
                        'title': 'Automated Sales Follow-up',
                        'description': 'Automatically send follow-up emails to prospects after initial contact',
                        'confidence': 0.8,
                        'potential_savings': '2 hours/week',
                        'implementation_effort': 'Low'
                    })
            
            if 'inventory_data' in context_data:
                inventory_data = context_data['inventory_data']
                low_stock_items = [item for item in inventory_data if item.get('current_stock', 0) < item.get('min_stock', 0)]
                if len(low_stock_items) > 0:
                    recommendations.append({
                        'type': 'inventory_automation',
                        'title': 'Automated Reorder System',
                        'description': 'Automatically generate purchase orders when stock levels fall below minimum',
                        'confidence': 0.9,
                        'potential_savings': '4 hours/week',
                        'implementation_effort': 'Medium'
                    })
            
            if 'customer_data' in context_data:
                customer_data = context_data['customer_data']
                inactive_customers = [c for c in customer_data if c.get('days_since_last_purchase', 0) > 90]
                if len(inactive_customers) > 10:
                    recommendations.append({
                        'type': 'customer_retention_automation',
                        'title': 'Automated Customer Retention Campaign',
                        'description': 'Automatically send re-engagement emails to inactive customers',
                        'confidence': 0.75,
                        'potential_savings': '3 hours/week',
                        'implementation_effort': 'Medium'
                    })
            
            logger.info(f"Generated {len(recommendations)} automation recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating automation recommendations: {str(e)}")
            return []
    
    def get_automation_rule_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all automation rules
        """
        try:
            total_rules = len(self.automation_rules)
            active_rules = len([r for r in self.automation_rules.values() if r.status == AutomationStatus.ACTIVE])
            total_executions = sum(rule.execution_count for rule in self.automation_rules.values())
            total_successes = sum(rule.success_count for rule in self.automation_rules.values())
            total_failures = sum(rule.failure_count for rule in self.automation_rules.values())
            
            success_rate = (total_successes / total_executions * 100) if total_executions > 0 else 0
            
            return {
                'total_rules': total_rules,
                'active_rules': active_rules,
                'inactive_rules': total_rules - active_rules,
                'total_executions': total_executions,
                'total_successes': total_successes,
                'total_failures': total_failures,
                'success_rate': success_rate,
                'average_executions_per_rule': total_executions / total_rules if total_rules > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting automation statistics: {str(e)}")
            return {}

# Global Intelligent Automation Engine instance
intelligent_automation_engine = IntelligentAutomationEngine()
