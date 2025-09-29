# Equipment DocType - Complete Equipment Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class Equipment(Document):
    def autoname(self):
        """Generate unique equipment ID"""
        if not self.equipment_id:
            self.equipment_id = make_autoname("EQ-.YYYY.-.MM.-.#####")
        self.name = self.equipment_id

    def validate(self):
        """Validate equipment data"""
        self.validate_equipment_data()
        self.set_defaults()
        self.validate_equipment_details()
        self.calculate_equipment_value()

    def before_save(self):
        """Process before saving"""
        self.update_equipment_settings()
        self.generate_equipment_insights()
        self.calculate_depreciation()

    def after_insert(self):
        """Process after inserting new equipment"""
        self.create_equipment_entries()
        self.setup_equipment_workflow()

    def on_update(self):
        """Process on equipment update"""
        self.update_equipment_analytics()
        self.sync_equipment_data()
        self.process_equipment_changes()

    def validate_equipment_data(self):
        """Validate equipment information"""
        if not self.equipment_name:
            frappe.throw(_("Equipment name is required"))
        
        if not self.equipment_type:
            frappe.throw(_("Equipment type is required"))
        
        if not self.purchase_date:
            frappe.throw(_("Purchase date is required"))
        
        if not self.purchase_value:
            frappe.throw(_("Purchase value is required"))

    def set_defaults(self):
        """Set default values for new equipment"""
        if not self.equipment_date:
            self.equipment_date = now()
        
        if not self.status:
            self.status = "Active"
        
        if not self.condition:
            self.condition = "Good"

    def validate_equipment_details(self):
        """Validate equipment details"""
        if self.serial_number:
            # Check for duplicate serial number
            existing_equipment = frappe.get_list("Equipment",
                filters={"serial_number": self.serial_number},
                fields=["name"]
            )
            
            if existing_equipment and existing_equipment[0].name != self.name:
                frappe.throw(_("Serial number {0} already exists").format(self.serial_number))

    def calculate_equipment_value(self):
        """Calculate equipment value"""
        if self.purchase_value and self.purchase_date:
            # Calculate depreciation
            self.calculate_depreciation()
            
            # Calculate current value
            self.current_value = self.purchase_value - self.total_depreciation
            
            # Calculate book value
            self.book_value = self.current_value

    def calculate_depreciation(self):
        """Calculate equipment depreciation"""
        if self.purchase_date and self.purchase_value:
            # Calculate age in years
            age_years = (now().date() - self.purchase_date).days / 365.25
            
            # Calculate depreciation based on method
            if self.depreciation_method == "Straight Line":
                self.calculate_straight_line_depreciation(age_years)
            elif self.depreciation_method == "Declining Balance":
                self.calculate_declining_balance_depreciation(age_years)
            elif self.depreciation_method == "Sum of Years":
                self.calculate_sum_of_years_depreciation(age_years)

    def calculate_straight_line_depreciation(self, age_years):
        """Calculate straight line depreciation"""
        if self.useful_life_years:
            annual_depreciation = self.purchase_value / self.useful_life_years
            self.total_depreciation = min(annual_depreciation * age_years, self.purchase_value)
            self.annual_depreciation = annual_depreciation

    def calculate_declining_balance_depreciation(self, age_years):
        """Calculate declining balance depreciation"""
        if self.depreciation_rate:
            remaining_value = self.purchase_value
            total_depreciation = 0
            
            for year in range(int(age_years)):
                year_depreciation = remaining_value * (self.depreciation_rate / 100)
                total_depreciation += year_depreciation
                remaining_value -= year_depreciation
            
            self.total_depreciation = min(total_depreciation, self.purchase_value)

    def calculate_sum_of_years_depreciation(self, age_years):
        """Calculate sum of years depreciation"""
        if self.useful_life_years:
            sum_of_years = (self.useful_life_years * (self.useful_life_years + 1)) / 2
            remaining_years = max(0, self.useful_life_years - age_years)
            
            depreciation_fraction = remaining_years / sum_of_years
            self.total_depreciation = self.purchase_value * (1 - depreciation_fraction)

    def create_equipment_entries(self):
        """Create equipment entries"""
        # Create equipment entry
        equipment_entry = frappe.new_doc("Equipment Entry")
        equipment_entry.equipment = self.name
        equipment_entry.equipment_name = self.equipment_name
        equipment_entry.equipment_type = self.equipment_type
        equipment_entry.serial_number = self.serial_number
        equipment_entry.purchase_value = self.purchase_value
        equipment_entry.current_value = self.current_value
        equipment_entry.status = self.status
        equipment_entry.save(ignore_permissions=True)

    def setup_equipment_workflow(self):
        """Setup equipment workflow"""
        # Update equipment workflow status
        workflow_data = {
            "workflow_name": f"Equipment Workflow - {self.equipment_id}",
            "workflow_type": "Equipment",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Equipment Workflow DocType
        if frappe.db.exists("Equipment Workflow", self.equipment_id):
            equipment_workflow = frappe.get_doc("Equipment Workflow", self.equipment_id)
            equipment_workflow.update(workflow_data)
            equipment_workflow.save(ignore_permissions=True)
        else:
            equipment_workflow = frappe.new_doc("Equipment Workflow")
            equipment_workflow.update(workflow_data)
            equipment_workflow.name = self.equipment_id
            equipment_workflow.insert(ignore_permissions=True)

    def update_equipment_settings(self):
        """Update equipment settings"""
        # Set equipment permissions
        self.set_equipment_permissions()
        
        # Update equipment workflow
        self.update_equipment_workflow()

    def set_equipment_permissions(self):
        """Set equipment permissions"""
        # Create equipment-specific roles
        equipment_roles = [
            f"Equipment - {self.equipment_id}",
            f"Type - {self.equipment_type}",
            f"Status - {self.status}"
        ]
        
        # Ensure roles exist
        for role_name in equipment_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_equipment_workflow(self):
        """Update equipment workflow"""
        # Update equipment workflow status
        workflow_data = {
            "workflow_name": f"Equipment Workflow - {self.equipment_id}",
            "workflow_type": "Equipment",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Equipment Workflow DocType
        if frappe.db.exists("Equipment Workflow", self.equipment_id):
            equipment_workflow = frappe.get_doc("Equipment Workflow", self.equipment_id)
            equipment_workflow.update(workflow_data)
            equipment_workflow.save(ignore_permissions=True)
        else:
            equipment_workflow = frappe.new_doc("Equipment Workflow")
            equipment_workflow.update(workflow_data)
            equipment_workflow.name = self.equipment_id
            equipment_workflow.insert(ignore_permissions=True)

    def generate_equipment_insights(self):
        """Generate equipment insights"""
        insights = {
            "equipment_id": self.equipment_id,
            "equipment_name": self.equipment_name,
            "equipment_type": self.equipment_type,
            "serial_number": self.serial_number,
            "purchase_date": self.purchase_date,
            "purchase_value": self.purchase_value,
            "current_value": self.current_value,
            "book_value": self.book_value,
            "total_depreciation": self.total_depreciation,
            "status": self.status,
            "condition": self.condition,
            "assigned_to": self.assigned_to,
            "location": self.location,
            "recommendations": self.generate_recommendations()
        }
        
        self.equipment_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate equipment recommendations"""
        recommendations = []
        
        # Maintenance recommendations
        if self.condition == "Poor":
            recommendations.append("Schedule immediate maintenance or replacement")
        
        if self.condition == "Fair":
            recommendations.append("Schedule preventive maintenance")
        
        # Depreciation recommendations
        if self.total_depreciation > self.purchase_value * 0.8:
            recommendations.append("Consider equipment replacement due to high depreciation")
        
        # Assignment recommendations
        if not self.assigned_to:
            recommendations.append("Assign equipment to an employee for better tracking")
        
        return recommendations

    def update_equipment_analytics(self):
        """Update equipment analytics"""
        # Update equipment analytics data
        analytics_data = {
            "analytics_name": f"Equipment Analytics - {self.equipment_id}",
            "analytics_type": "Equipment Analytics",
            "metrics": {
                "equipment_id": self.equipment_id,
                "equipment_name": self.equipment_name,
                "equipment_type": self.equipment_type,
                "purchase_value": self.purchase_value,
                "current_value": self.current_value,
                "total_depreciation": self.total_depreciation,
                "status": self.status,
                "condition": self.condition
            },
            "insights": self.generate_equipment_insights(),
            "last_updated": now()
        }
        
        # Update or create Equipment Analytics DocType
        if frappe.db.exists("Equipment Analytics", self.equipment_id):
            equipment_analytics = frappe.get_doc("Equipment Analytics", self.equipment_id)
            equipment_analytics.update(analytics_data)
            equipment_analytics.save(ignore_permissions=True)
        else:
            equipment_analytics = frappe.new_doc("Equipment Analytics")
            equipment_analytics.update(analytics_data)
            equipment_analytics.name = self.equipment_id
            equipment_analytics.insert(ignore_permissions=True)

    def sync_equipment_data(self):
        """Sync equipment data across systems"""
        # Sync with external asset management systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_equipment_changes(self):
        """Process equipment changes"""
        # Log changes
        self.log_equipment_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_equipment_changes(self):
        """Log equipment changes"""
        frappe.get_doc({
            "doctype": "Equipment Change Log",
            "equipment": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Equipment {self.equipment_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update employee equipment records
        self.update_employee_equipment_records()

    def update_employee_equipment_records(self):
        """Update employee equipment records"""
        if self.assigned_to:
            # Update employee equipment assignment
            frappe.db.sql("""
                UPDATE `tabEmployee`
                SET assigned_equipment = (
                    SELECT COUNT(*) FROM `tabEquipment`
                    WHERE assigned_to = %s AND status = 'Active'
                )
                WHERE name = %s
            """, (self.assigned_to, self.assigned_to))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify HR team
        self.notify_hr_team()
        
        # Notify assigned employee
        self.notify_assigned_employee()

    def notify_hr_team(self):
        """Notify HR team"""
        frappe.get_doc({
            "doctype": "Equipment Notification",
            "equipment": self.name,
            "notification_type": "Equipment Update",
            "message": f"Equipment {self.equipment_id} has been updated",
            "recipients": "HR Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_assigned_employee(self):
        """Notify assigned employee"""
        if self.assigned_to:
            frappe.get_doc({
                "doctype": "Equipment Notification",
                "equipment": self.name,
                "notification_type": "Equipment Update",
                "message": f"Equipment {self.equipment_id} has been updated",
                "recipients": self.assigned_to,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync equipment data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_equipment_dashboard_data(self):
        """Get equipment dashboard data"""
        return {
            "equipment_id": self.equipment_id,
            "equipment_name": self.equipment_name,
            "equipment_type": self.equipment_type,
            "serial_number": self.serial_number,
            "purchase_date": self.purchase_date,
            "purchase_value": self.purchase_value,
            "current_value": self.current_value,
            "book_value": self.book_value,
            "total_depreciation": self.total_depreciation,
            "status": self.status,
            "condition": self.condition,
            "assigned_to": self.assigned_to,
            "location": self.location,
            "insights": self.generate_equipment_insights()
        }

    @frappe.whitelist()
    def assign_equipment(self, employee):
        """Assign equipment to employee"""
        if self.status != "Active":
            frappe.throw(_("Only active equipment can be assigned"))
        
        if self.assigned_to:
            frappe.throw(_("Equipment is already assigned to {0}").format(self.assigned_to))
        
        self.assigned_to = employee
        self.assigned_date = now()
        self.assigned_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Equipment {0} assigned to {1}").format(self.equipment_id, employee))
        return self.as_dict()

    @frappe.whitelist()
    def unassign_equipment(self):
        """Unassign equipment from employee"""
        if not self.assigned_to:
            frappe.throw(_("Equipment is not assigned to anyone"))
        
        self.assigned_to = None
        self.assigned_date = None
        self.assigned_by = None
        self.save()
        
        frappe.msgprint(_("Equipment {0} unassigned").format(self.equipment_id))
        return self.as_dict()

    @frappe.whitelist()
    def transfer_equipment(self, new_employee):
        """Transfer equipment to another employee"""
        if not self.assigned_to:
            frappe.throw(_("Equipment is not assigned to anyone"))
        
        old_employee = self.assigned_to
        self.assigned_to = new_employee
        self.assigned_date = now()
        self.assigned_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Equipment {0} transferred from {1} to {2}").format(self.equipment_id, old_employee, new_employee))
        return self.as_dict()

    @frappe.whitelist()
    def update_condition(self, condition, notes=None):
        """Update equipment condition"""
        self.condition = condition
        if notes:
            self.condition_notes = notes
        self.condition_updated_date = now()
        self.condition_updated_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Equipment {0} condition updated to {1}").format(self.equipment_id, condition))
        return self.as_dict()

    @frappe.whitelist()
    def schedule_maintenance(self, maintenance_date, maintenance_type, description=None):
        """Schedule equipment maintenance"""
        maintenance = frappe.new_doc("Equipment Maintenance")
        maintenance.equipment = self.name
        maintenance.maintenance_date = maintenance_date
        maintenance.maintenance_type = maintenance_type
        maintenance.description = description
        maintenance.status = "Scheduled"
        maintenance.save(ignore_permissions=True)
        
        frappe.msgprint(_("Maintenance scheduled for equipment {0} on {1}").format(self.equipment_id, maintenance_date))
        return self.as_dict()

    @frappe.whitelist()
    def retire_equipment(self, retirement_date=None, retirement_reason=None):
        """Retire equipment"""
        if self.status == "Retired":
            frappe.throw(_("Equipment is already retired"))
        
        self.status = "Retired"
        self.retirement_date = retirement_date or now()
        self.retirement_reason = retirement_reason
        self.retired_by = frappe.session.user
        
        # Unassign if assigned
        if self.assigned_to:
            self.assigned_to = None
            self.assigned_date = None
            self.assigned_by = None
        
        self.save()
        
        frappe.msgprint(_("Equipment {0} retired on {1}").format(self.equipment_id, self.retirement_date))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_equipment(self):
        """Duplicate equipment"""
        new_equipment = frappe.copy_doc(self)
        new_equipment.equipment_id = None
        new_equipment.serial_number = None
        new_equipment.status = "Draft"
        new_equipment.assigned_to = None
        new_equipment.assigned_date = None
        new_equipment.assigned_by = None
        new_equipment.save(ignore_permissions=True)
        
        frappe.msgprint(_("Equipment duplicated as {0}").format(new_equipment.equipment_id))
        return new_equipment.as_dict()
