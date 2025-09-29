# Leave Request DocType - Complete Leave Management System

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../core'))

from database_manager import db, get_list, get_value, set_value, exists, count, sql
from frappe_replacement import (
    get_doc, new_doc, get_current_user, _, now, get_datetime, 
    add_days, get_time, flt, date_diff, make_autoname, 
    validate, throw, msgprint, has_permission
)
import json
from datetime import datetime, timedelta
import requests

class LeaveRequest:
    def autoname(self):
        """Generate unique leave request ID"""
        if not self.leave_request_id:
            self.leave_request_id = make_autoname("LR-.YYYY.-.MM.-.#####")
        self.name = self.leave_request_id

    def validate(self):
        """Validate leave request data"""
        self.validate_leave_request_data()
        self.set_defaults()
        self.validate_employee_data()
        self.validate_leave_balance()
        self.validate_leave_period()

    def before_save(self):
        """Process before saving"""
        self.update_leave_request_settings()
        self.generate_leave_request_insights()
        self.calculate_leave_days()

    def after_insert(self):
        """Process after inserting new leave request"""
        self.create_leave_request_entries()
        self.setup_leave_request_workflow()

    def on_update(self):
        """Process on leave request update"""
        self.update_leave_request_analytics()
        self.sync_leave_request_data()
        self.process_leave_request_changes()

    def validate_leave_request_data(self):
        """Validate leave request information"""
        if not self.employee:
            throw(_("Employee is required"))
        
        if not self.leave_type:
            throw(_("Leave type is required"))
        
        if not self.from_date:
            throw(_("From date is required"))
        
        if not self.to_date:
            throw(_("To date is required"))

    def set_defaults(self):
        """Set default values for new leave request"""
        if not self.leave_request_date:
            self.leave_request_date = now()
        
        if not self.status:
            self.status = "Draft"
        
        if not self.requested_by:
            self.requested_by = get_current_user()

    def validate_employee_data(self):
        """Validate employee information"""
        if not exists("Employee", {"name": self.employee}):
            throw(_("Employee {0} does not exist").format(self.employee))

    def validate_leave_balance(self):
        """Validate leave balance"""
        employee = get_doc("Employee", self.employee)
        leave_balance = self.get_leave_balance()
        
        if leave_balance < self.total_days:
            throw(_("Insufficient leave balance. Available: {0}, Requested: {1}").format(leave_balance, self.total_days))

    def validate_leave_period(self):
        """Validate leave period"""
        if self.from_date > self.to_date:
            throw(_("From date cannot be greater than to date"))
        
        # Check for overlapping leave requests
        overlapping_requests = get_list("Leave Request",
            filters={
                "employee": self.employee,
                "status": ["in", ["Approved", "Pending"]],
                "from_date": ["<=", self.to_date],
                "to_date": [">=", self.from_date]
            }
        )
        
        if overlapping_requests:
            throw(_("Leave request overlaps with existing approved/pending requests"))

    def calculate_leave_days(self):
        """Calculate total leave days"""
        if self.from_date and self.to_date:
            self.total_days = date_diff(self.to_date, self.from_date) + 1
            
            # Calculate working days if required
            if self.leave_type == "Sick Leave" or self.leave_type == "Personal Leave":
                self.working_days = self.calculate_working_days()
            else:
                self.working_days = self.total_days

    def calculate_working_days(self):
        """Calculate working days excluding weekends"""
        working_days = 0
        current_date = self.from_date
        
        while current_date <= self.to_date:
            # Check if it's a working day (Monday to Friday)
            if current_date.weekday() < 5:  # 0-4 for Monday-Friday
                working_days += 1
            current_date = add_days(current_date, 1)
        
        return working_days

    def get_leave_balance(self):
        """Get employee leave balance"""
        # Get leave allocation for the employee
        leave_allocation = get_doc("Leave Allocation", {
            "employee": self.employee,
            "leave_type": self.leave_type,
            "docstatus": 1
        })
        
        if leave_allocation:
            return leave_allocation.new_leaves_allocated - leave_allocation.total_leaves_taken
        else:
            return 0

    def create_leave_request_entries(self):
        """Create leave request entries"""
        # Create leave request entry
        leave_entry = new_doc("Leave Request Entry")
        leave_entry.leave_request = self.name
        leave_entry.employee = self.employee
        leave_entry.leave_type = self.leave_type
        leave_entry.from_date = self.from_date
        leave_entry.to_date = self.to_date
        leave_entry.total_days = self.total_days
        leave_entry.working_days = self.working_days
        leave_entry.status = self.status
        leave_entry.save(ignore_permissions=True)

    def setup_leave_request_workflow(self):
        """Setup leave request workflow"""
        # Update leave request workflow status
        workflow_data = {
            "workflow_name": f"Leave Request Workflow - {self.leave_request_id}",
            "workflow_type": "Leave Request",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Approved", "status": "Pending"}
            ]
        }
        
        # Update or create Leave Request Workflow DocType
        if exists("Leave Request Workflow", self.leave_request_id):
            leave_workflow = get_doc("Leave Request Workflow", self.leave_request_id)
            leave_workflow.update(workflow_data)
            leave_workflow.save(ignore_permissions=True)
        else:
            leave_workflow = new_doc("Leave Request Workflow")
            leave_workflow.update(workflow_data)
            leave_workflow.name = self.leave_request_id
            leave_workflow.insert(ignore_permissions=True)

    def update_leave_request_settings(self):
        """Update leave request settings"""
        # Set leave request permissions
        self.set_leave_request_permissions()
        
        # Update leave request workflow
        self.update_leave_request_workflow()

    def set_leave_request_permissions(self):
        """Set leave request permissions"""
        # Create leave request-specific roles
        leave_roles = [
            f"Leave Request - {self.leave_request_id}",
            f"Employee - {self.employee}",
            f"Leave Type - {self.leave_type}"
        ]
        
        # Ensure roles exist
        for role_name in leave_roles:
            if not exists("Role", role_name):
                role = new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_leave_request_workflow(self):
        """Update leave request workflow"""
        # Update leave request workflow status
        workflow_data = {
            "workflow_name": f"Leave Request Workflow - {self.leave_request_id}",
            "workflow_type": "Leave Request",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Approved", "status": "Pending"}
            ]
        }
        
        # Update or create Leave Request Workflow DocType
        if exists("Leave Request Workflow", self.leave_request_id):
            leave_workflow = get_doc("Leave Request Workflow", self.leave_request_id)
            leave_workflow.update(workflow_data)
            leave_workflow.save(ignore_permissions=True)
        else:
            leave_workflow = new_doc("Leave Request Workflow")
            leave_workflow.update(workflow_data)
            leave_workflow.name = self.leave_request_id
            leave_workflow.insert(ignore_permissions=True)

    def generate_leave_request_insights(self):
        """Generate leave request insights"""
        insights = {
            "leave_request_id": self.leave_request_id,
            "employee": self.employee,
            "leave_type": self.leave_type,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "total_days": self.total_days,
            "working_days": self.working_days,
            "status": self.status,
            "leave_balance": self.get_leave_balance(),
            "recommendations": self.generate_recommendations()
        }
        
        self.leave_request_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate leave request recommendations"""
        recommendations = []
        
        # Leave balance recommendations
        leave_balance = self.get_leave_balance()
        if leave_balance < 5:
            recommendations.append("Consider leave balance management for future requests")
        
        # Leave type recommendations
        if self.leave_type == "Sick Leave" and self.total_days > 3:
            recommendations.append("Consider medical certificate for extended sick leave")
        
        # Period recommendations
        if self.total_days > 10:
            recommendations.append("Consider advance notice for long leave periods")
        
        return recommendations

    def update_leave_request_analytics(self):
        """Update leave request analytics"""
        # Update leave request analytics data
        analytics_data = {
            "analytics_name": f"Leave Request Analytics - {self.leave_request_id}",
            "analytics_type": "Leave Request Analytics",
            "metrics": {
                "leave_request_id": self.leave_request_id,
                "employee": self.employee,
                "leave_type": self.leave_type,
                "total_days": self.total_days,
                "working_days": self.working_days,
                "status": self.status
            },
            "insights": self.generate_leave_request_insights(),
            "last_updated": now()
        }
        
        # Update or create Leave Request Analytics DocType
        if exists("Leave Request Analytics", self.leave_request_id):
            leave_analytics = get_doc("Leave Request Analytics", self.leave_request_id)
            leave_analytics.update(analytics_data)
            leave_analytics.save(ignore_permissions=True)
        else:
            leave_analytics = new_doc("Leave Request Analytics")
            leave_analytics.update(analytics_data)
            leave_analytics.name = self.leave_request_id
            leave_analytics.insert(ignore_permissions=True)

    def sync_leave_request_data(self):
        """Sync leave request data across systems"""
        # Sync with external HR systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_leave_request_changes(self):
        """Process leave request changes"""
        # Log changes
        self.log_leave_request_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_leave_request_changes(self):
        """Log leave request changes"""
        get_doc({
            "doctype": "Leave Request Change Log",
            "leave_request": self.name,
            "changed_by": get_current_user(),
            "change_date": now(),
            "description": f"Leave Request {self.leave_request_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update employee leave records
        self.update_employee_leave_records()

    def update_employee_leave_records(self):
        """Update employee leave records"""
        # Update employee leave allocation
        db.execute("""
            UPDATE `tabLeave Allocation`
            SET total_leaves_taken = total_leaves_taken + %s
            WHERE employee = %s AND leave_type = %s
        """, (self.total_days, self.employee, self.leave_type))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify HR team
        self.notify_hr_team()
        
        # Notify manager
        self.notify_manager()

    def notify_hr_team(self):
        """Notify HR team"""
        get_doc({
            "doctype": "Leave Request Notification",
            "leave_request": self.name,
            "notification_type": "Leave Request Update",
            "message": f"Leave Request {self.leave_request_id} has been updated",
            "recipients": "HR Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_manager(self):
        """Notify manager"""
        employee = get_doc("Employee", self.employee)
        if employee.reports_to:
            get_doc({
                "doctype": "Leave Request Notification",
                "leave_request": self.name,
                "notification_type": "Leave Request Update",
                "message": f"Leave Request {self.leave_request_id} has been updated",
                "recipients": employee.reports_to,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync leave request data with external system"""
        # Implementation for external system sync
        pass

    # API endpoint
    def get_leave_request_dashboard_data(self):
        """Get leave request dashboard data"""
        return {
            "leave_request_id": self.leave_request_id,
            "employee": self.employee,
            "leave_type": self.leave_type,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "total_days": self.total_days,
            "working_days": self.working_days,
            "status": self.status,
            "leave_balance": self.get_leave_balance(),
            "insights": self.generate_leave_request_insights()
        }

    # API endpoint
    def approve_leave_request(self):
        """Approve leave request"""
        if self.status != "Pending":
            throw(_("Only pending leave requests can be approved"))
        
        self.status = "Approved"
        self.approved_by = get_current_user()
        self.approved_date = now()
        self.save()
        
        # Update leave allocation
        self.update_leave_allocation()
        
        msgprint(_("Leave Request {0} approved").format(self.leave_request_id))
        return self.as_dict()

    def update_leave_allocation(self):
        """Update leave allocation"""
        # Update leave allocation
        db.execute("""
            UPDATE `tabLeave Allocation`
            SET total_leaves_taken = total_leaves_taken + %s
            WHERE employee = %s AND leave_type = %s
        """, (self.total_days, self.employee, self.leave_type))

    # API endpoint
    def reject_leave_request(self, reason=None):
        """Reject leave request"""
        if self.status != "Pending":
            throw(_("Only pending leave requests can be rejected"))
        
        self.status = "Rejected"
        self.rejected_by = get_current_user()
        self.rejected_date = now()
        self.rejection_reason = reason
        self.save()
        
        msgprint(_("Leave Request {0} rejected").format(self.leave_request_id))
        return self.as_dict()

    # API endpoint
    def cancel_leave_request(self):
        """Cancel leave request"""
        if self.status == "Approved":
            # Reverse leave allocation
            self.reverse_leave_allocation()
        
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.cancelled_by = get_current_user()
        self.save()
        
        msgprint(_("Leave Request {0} cancelled").format(self.leave_request_id))
        return self.as_dict()

    def reverse_leave_allocation(self):
        """Reverse leave allocation for cancelled leave request"""
        db.execute("""
            UPDATE `tabLeave Allocation`
            SET total_leaves_taken = total_leaves_taken - %s
            WHERE employee = %s AND leave_type = %s
        """, (self.total_days, self.employee, self.leave_type))

    # API endpoint
    def duplicate_leave_request(self):
        """Duplicate leave request"""
        new_leave_request = copy_doc(self)
        new_leave_request.leave_request_id = None
        new_leave_request.status = "Draft"
        new_leave_request.leave_request_date = now()
        new_leave_request.save(ignore_permissions=True)
        
        msgprint(_("Leave Request duplicated as {0}").format(new_leave_request.leave_request_id))
        return new_leave_request.as_dict()
