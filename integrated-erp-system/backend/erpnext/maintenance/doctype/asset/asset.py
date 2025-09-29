# Asset DocType - Complete Asset Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class Asset(Document):
    def autoname(self):
        """Generate unique asset ID"""
        if not self.asset_id:
            self.asset_id = make_autoname("AST-.YYYY.-.MM.-.#####")
        self.name = self.asset_id

    def validate(self):
        """Validate asset data"""
        self.validate_asset_data()
        self.set_defaults()
        self.validate_asset_details()
        self.calculate_asset_value()

    def before_save(self):
        """Process before saving"""
        self.update_asset_settings()
        self.generate_asset_insights()
        self.calculate_depreciation()

    def after_insert(self):
        """Process after inserting new asset"""
        self.create_asset_entries()
        self.setup_asset_workflow()

    def on_update(self):
        """Process on asset update"""
        self.update_asset_analytics()
        self.sync_asset_data()
        self.process_asset_changes()

    def validate_asset_data(self):
        """Validate asset information"""
        if not self.asset_name:
            frappe.throw(_("Asset name is required"))
        
        if not self.asset_type:
            frappe.throw(_("Asset type is required"))
        
        if not self.purchase_date:
            frappe.throw(_("Purchase date is required"))
        
        if not self.purchase_value:
            frappe.throw(_("Purchase value is required"))

    def set_defaults(self):
        """Set default values for new asset"""
        if not self.asset_date:
            self.asset_date = now()
        
        if not self.status:
            self.status = "Active"
        
        if not self.condition:
            self.condition = "Good"

    def validate_asset_details(self):
        """Validate asset details"""
        if self.serial_number:
            # Check for duplicate serial number
            existing_asset = frappe.get_list("Asset",
                filters={"serial_number": self.serial_number},
                fields=["name"]
            )
            
            if existing_asset and existing_asset[0].name != self.name:
                frappe.throw(_("Serial number {0} already exists").format(self.serial_number))

    def calculate_asset_value(self):
        """Calculate asset value"""
        if self.purchase_value and self.purchase_date:
            # Calculate depreciation
            self.calculate_depreciation()
            
            # Calculate current value
            self.current_value = self.purchase_value - self.total_depreciation
            
            # Calculate book value
            self.book_value = self.current_value

    def calculate_depreciation(self):
        """Calculate asset depreciation"""
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

    def create_asset_entries(self):
        """Create asset entries"""
        # Create asset entry
        asset_entry = frappe.new_doc("Asset Entry")
        asset_entry.asset = self.name
        asset_entry.asset_name = self.asset_name
        asset_entry.asset_type = self.asset_type
        asset_entry.serial_number = self.serial_number
        asset_entry.purchase_value = self.purchase_value
        asset_entry.current_value = self.current_value
        asset_entry.status = self.status
        asset_entry.save(ignore_permissions=True)

    def setup_asset_workflow(self):
        """Setup asset workflow"""
        # Update asset workflow status
        workflow_data = {
            "workflow_name": f"Asset Workflow - {self.asset_id}",
            "workflow_type": "Asset",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Asset Workflow DocType
        if frappe.db.exists("Asset Workflow", self.asset_id):
            asset_workflow = frappe.get_doc("Asset Workflow", self.asset_id)
            asset_workflow.update(workflow_data)
            asset_workflow.save(ignore_permissions=True)
        else:
            asset_workflow = frappe.new_doc("Asset Workflow")
            asset_workflow.update(workflow_data)
            asset_workflow.name = self.asset_id
            asset_workflow.insert(ignore_permissions=True)

    def update_asset_settings(self):
        """Update asset settings"""
        # Set asset permissions
        self.set_asset_permissions()
        
        # Update asset workflow
        self.update_asset_workflow()

    def set_asset_permissions(self):
        """Set asset permissions"""
        # Create asset-specific roles
        asset_roles = [
            f"Asset - {self.asset_id}",
            f"Type - {self.asset_type}",
            f"Status - {self.status}"
        ]
        
        # Ensure roles exist
        for role_name in asset_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_asset_workflow(self):
        """Update asset workflow"""
        # Update asset workflow status
        workflow_data = {
            "workflow_name": f"Asset Workflow - {self.asset_id}",
            "workflow_type": "Asset",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Asset Workflow DocType
        if frappe.db.exists("Asset Workflow", self.asset_id):
            asset_workflow = frappe.get_doc("Asset Workflow", self.asset_id)
            asset_workflow.update(workflow_data)
            asset_workflow.save(ignore_permissions=True)
        else:
            asset_workflow = frappe.new_doc("Asset Workflow")
            asset_workflow.update(workflow_data)
            asset_workflow.name = self.asset_id
            asset_workflow.insert(ignore_permissions=True)

    def generate_asset_insights(self):
        """Generate asset insights"""
        insights = {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
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
        
        self.asset_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate asset recommendations"""
        recommendations = []
        
        # Maintenance recommendations
        if self.condition == "Poor":
            recommendations.append("Schedule immediate maintenance or replacement")
        
        if self.condition == "Fair":
            recommendations.append("Schedule preventive maintenance")
        
        # Depreciation recommendations
        if self.total_depreciation > self.purchase_value * 0.8:
            recommendations.append("Consider asset replacement due to high depreciation")
        
        # Assignment recommendations
        if not self.assigned_to:
            recommendations.append("Assign asset to an employee for better tracking")
        
        return recommendations

    def update_asset_analytics(self):
        """Update asset analytics"""
        # Update asset analytics data
        analytics_data = {
            "analytics_name": f"Asset Analytics - {self.asset_id}",
            "analytics_type": "Asset Analytics",
            "metrics": {
                "asset_id": self.asset_id,
                "asset_name": self.asset_name,
                "asset_type": self.asset_type,
                "purchase_value": self.purchase_value,
                "current_value": self.current_value,
                "total_depreciation": self.total_depreciation,
                "status": self.status,
                "condition": self.condition
            },
            "insights": self.generate_asset_insights(),
            "last_updated": now()
        }
        
        # Update or create Asset Analytics DocType
        if frappe.db.exists("Asset Analytics", self.asset_id):
            asset_analytics = frappe.get_doc("Asset Analytics", self.asset_id)
            asset_analytics.update(analytics_data)
            asset_analytics.save(ignore_permissions=True)
        else:
            asset_analytics = frappe.new_doc("Asset Analytics")
            asset_analytics.update(analytics_data)
            asset_analytics.name = self.asset_id
            asset_analytics.insert(ignore_permissions=True)

    def sync_asset_data(self):
        """Sync asset data across systems"""
        # Sync with external asset management systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_asset_changes(self):
        """Process asset changes"""
        # Log changes
        self.log_asset_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_asset_changes(self):
        """Log asset changes"""
        frappe.get_doc({
            "doctype": "Asset Change Log",
            "asset": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Asset {self.asset_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update employee asset records
        self.update_employee_asset_records()

    def update_employee_asset_records(self):
        """Update employee asset records"""
        if self.assigned_to:
            # Update employee asset assignment
            frappe.db.sql("""
                UPDATE `tabEmployee`
                SET assigned_assets = (
                    SELECT COUNT(*) FROM `tabAsset`
                    WHERE assigned_to = %s AND status = 'Active'
                )
                WHERE name = %s
            """, (self.assigned_to, self.assigned_to))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify maintenance team
        self.notify_maintenance_team()
        
        # Notify assigned employee
        self.notify_assigned_employee()

    def notify_maintenance_team(self):
        """Notify maintenance team"""
        frappe.get_doc({
            "doctype": "Asset Notification",
            "asset": self.name,
            "notification_type": "Asset Update",
            "message": f"Asset {self.asset_id} has been updated",
            "recipients": "Maintenance Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_assigned_employee(self):
        """Notify assigned employee"""
        if self.assigned_to:
            frappe.get_doc({
                "doctype": "Asset Notification",
                "asset": self.name,
                "notification_type": "Asset Update",
                "message": f"Asset {self.asset_id} has been updated",
                "recipients": self.assigned_to,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync asset data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_asset_dashboard_data(self):
        """Get asset dashboard data"""
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
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
            "insights": self.generate_asset_insights()
        }

    @frappe.whitelist()
    def assign_asset(self, employee):
        """Assign asset to employee"""
        if self.status != "Active":
            frappe.throw(_("Only active assets can be assigned"))
        
        if self.assigned_to:
            frappe.throw(_("Asset is already assigned to {0}").format(self.assigned_to))
        
        self.assigned_to = employee
        self.assigned_date = now()
        self.assigned_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Asset {0} assigned to {1}").format(self.asset_id, employee))
        return self.as_dict()

    @frappe.whitelist()
    def unassign_asset(self):
        """Unassign asset from employee"""
        if not self.assigned_to:
            frappe.throw(_("Asset is not assigned to anyone"))
        
        self.assigned_to = None
        self.assigned_date = None
        self.assigned_by = None
        self.save()
        
        frappe.msgprint(_("Asset {0} unassigned").format(self.asset_id))
        return self.as_dict()

    @frappe.whitelist()
    def transfer_asset(self, new_employee):
        """Transfer asset to another employee"""
        if not self.assigned_to:
            frappe.throw(_("Asset is not assigned to anyone"))
        
        old_employee = self.assigned_to
        self.assigned_to = new_employee
        self.assigned_date = now()
        self.assigned_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Asset {0} transferred from {1} to {2}").format(self.asset_id, old_employee, new_employee))
        return self.as_dict()

    @frappe.whitelist()
    def update_condition(self, condition, notes=None):
        """Update asset condition"""
        self.condition = condition
        if notes:
            self.condition_notes = notes
        self.condition_updated_date = now()
        self.condition_updated_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Asset {0} condition updated to {1}").format(self.asset_id, condition))
        return self.as_dict()

    @frappe.whitelist()
    def schedule_maintenance(self, maintenance_date, maintenance_type, description=None):
        """Schedule asset maintenance"""
        maintenance = frappe.new_doc("Asset Maintenance")
        maintenance.asset = self.name
        maintenance.maintenance_date = maintenance_date
        maintenance.maintenance_type = maintenance_type
        maintenance.description = description
        maintenance.status = "Scheduled"
        maintenance.save(ignore_permissions=True)
        
        frappe.msgprint(_("Maintenance scheduled for asset {0} on {1}").format(self.asset_id, maintenance_date))
        return self.as_dict()

    @frappe.whitelist()
    def retire_asset(self, retirement_date=None, retirement_reason=None):
        """Retire asset"""
        if self.status == "Retired":
            frappe.throw(_("Asset is already retired"))
        
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
        
        frappe.msgprint(_("Asset {0} retired on {1}").format(self.asset_id, self.retirement_date))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_asset(self):
        """Duplicate asset"""
        new_asset = frappe.copy_doc(self)
        new_asset.asset_id = None
        new_asset.serial_number = None
        new_asset.status = "Draft"
        new_asset.assigned_to = None
        new_asset.assigned_date = None
        new_asset.assigned_by = None
        new_asset.save(ignore_permissions=True)
        
        frappe.msgprint(_("Asset duplicated as {0}").format(new_asset.asset_id))
        return new_asset.as_dict()
