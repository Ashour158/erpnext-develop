# Work Order DocType - Complete Work Order Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class WorkOrder(Document):
    def autoname(self):
        """Generate unique work order ID"""
        if not self.work_order_id:
            self.work_order_id = make_autoname("WO-.YYYY.-.MM.-.#####")
        self.name = self.work_order_id

    def validate(self):
        """Validate work order data"""
        self.validate_work_order_data()
        self.set_defaults()
        self.validate_asset_data()
        self.validate_technician_data()
        self.calculate_work_order_costs()

    def before_save(self):
        """Process before saving"""
        self.update_work_order_settings()
        self.generate_work_order_insights()
        self.calculate_work_order_duration()

    def after_insert(self):
        """Process after inserting new work order"""
        self.create_work_order_entries()
        self.setup_work_order_workflow()

    def on_update(self):
        """Process on work order update"""
        self.update_work_order_analytics()
        self.sync_work_order_data()
        self.process_work_order_changes()

    def validate_work_order_data(self):
        """Validate work order information"""
        if not self.work_order_title:
            frappe.throw(_("Work order title is required"))
        
        if not self.asset:
            frappe.throw(_("Asset is required"))
        
        if not self.work_order_type:
            frappe.throw(_("Work order type is required"))
        
        if not self.priority:
            frappe.throw(_("Priority is required"))

    def set_defaults(self):
        """Set default values for new work order"""
        if not self.work_order_date:
            self.work_order_date = now()
        
        if not self.status:
            self.status = "Open"
        
        if not self.work_order_type:
            self.work_order_type = "Repair"
        
        if not self.priority:
            self.priority = "Medium"

    def validate_asset_data(self):
        """Validate asset information"""
        if not frappe.db.exists("Asset", self.asset):
            frappe.throw(_("Asset {0} does not exist").format(self.asset))

    def validate_technician_data(self):
        """Validate technician information"""
        if self.assigned_technician:
            if not frappe.db.exists("User", self.assigned_technician):
                frappe.throw(_("Technician {0} does not exist").format(self.assigned_technician))

    def calculate_work_order_costs(self):
        """Calculate work order costs"""
        self.total_labor_cost = 0
        self.total_material_cost = 0
        self.total_cost = 0

        # Calculate labor costs
        for labor in self.labor_items:
            labor.total_cost = labor.hours * labor.hourly_rate
            self.total_labor_cost += labor.total_cost

        # Calculate material costs
        for material in self.material_items:
            material.total_cost = material.quantity * material.unit_cost
            self.total_material_cost += material.total_cost

        # Calculate total cost
        self.total_cost = self.total_labor_cost + self.total_material_cost

    def calculate_work_order_duration(self):
        """Calculate work order duration"""
        if self.scheduled_start_date and self.scheduled_end_date:
            self.duration_days = (self.scheduled_end_date - self.scheduled_start_date).days + 1
        else:
            self.duration_days = 0

    def create_work_order_entries(self):
        """Create work order entries"""
        # Create work order entry
        work_order_entry = frappe.new_doc("Work Order Entry")
        work_order_entry.work_order = self.name
        work_order_entry.work_order_title = self.work_order_title
        work_order_entry.asset = self.asset
        work_order_entry.work_order_type = self.work_order_type
        work_order_entry.priority = self.priority
        work_order_entry.status = self.status
        work_order_entry.save(ignore_permissions=True)

    def setup_work_order_workflow(self):
        """Setup work order workflow"""
        # Update work order workflow status
        workflow_data = {
            "workflow_name": f"Work Order Workflow - {self.work_order_id}",
            "workflow_type": "Work Order",
            "steps": [
                {"step": "Open", "status": "Completed"},
                {"step": "In Progress", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create Work Order Workflow DocType
        if frappe.db.exists("Work Order Workflow", self.work_order_id):
            work_order_workflow = frappe.get_doc("Work Order Workflow", self.work_order_id)
            work_order_workflow.update(workflow_data)
            work_order_workflow.save(ignore_permissions=True)
        else:
            work_order_workflow = frappe.new_doc("Work Order Workflow")
            work_order_workflow.update(workflow_data)
            work_order_workflow.name = self.work_order_id
            work_order_workflow.insert(ignore_permissions=True)

    def update_work_order_settings(self):
        """Update work order settings"""
        # Set work order permissions
        self.set_work_order_permissions()
        
        # Update work order workflow
        self.update_work_order_workflow()

    def set_work_order_permissions(self):
        """Set work order permissions"""
        # Create work order-specific roles
        work_order_roles = [
            f"Work Order - {self.work_order_id}",
            f"Asset - {self.asset}",
            f"Type - {self.work_order_type}"
        ]
        
        # Ensure roles exist
        for role_name in work_order_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_work_order_workflow(self):
        """Update work order workflow"""
        # Update work order workflow status
        workflow_data = {
            "workflow_name": f"Work Order Workflow - {self.work_order_id}",
            "workflow_type": "Work Order",
            "steps": [
                {"step": "Open", "status": "Completed"},
                {"step": "In Progress", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create Work Order Workflow DocType
        if frappe.db.exists("Work Order Workflow", self.work_order_id):
            work_order_workflow = frappe.get_doc("Work Order Workflow", self.work_order_id)
            work_order_workflow.update(workflow_data)
            work_order_workflow.save(ignore_permissions=True)
        else:
            work_order_workflow = frappe.new_doc("Work Order Workflow")
            work_order_workflow.update(workflow_data)
            work_order_workflow.name = self.work_order_id
            work_order_workflow.insert(ignore_permissions=True)

    def generate_work_order_insights(self):
        """Generate work order insights"""
        insights = {
            "work_order_id": self.work_order_id,
            "work_order_title": self.work_order_title,
            "asset": self.asset,
            "work_order_type": self.work_order_type,
            "priority": self.priority,
            "status": self.status,
            "assigned_technician": self.assigned_technician,
            "scheduled_start_date": self.scheduled_start_date,
            "scheduled_end_date": self.scheduled_end_date,
            "duration_days": self.duration_days,
            "total_cost": self.total_cost,
            "total_labor_cost": self.total_labor_cost,
            "total_material_cost": self.total_material_cost,
            "recommendations": self.generate_recommendations()
        }
        
        self.work_order_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate work order recommendations"""
        recommendations = []
        
        # Priority recommendations
        if self.priority == "High":
            recommendations.append("Consider expediting this work order due to high priority")
        
        # Cost recommendations
        if self.total_cost > 10000:
            recommendations.append("Consider cost optimization for high-value work orders")
        
        # Duration recommendations
        if self.duration_days > 30:
            recommendations.append("Consider breaking down long-duration work orders")
        
        # Technician recommendations
        if not self.assigned_technician:
            recommendations.append("Assign a technician to this work order")
        
        return recommendations

    def update_work_order_analytics(self):
        """Update work order analytics"""
        # Update work order analytics data
        analytics_data = {
            "analytics_name": f"Work Order Analytics - {self.work_order_id}",
            "analytics_type": "Work Order Analytics",
            "metrics": {
                "work_order_id": self.work_order_id,
                "work_order_title": self.work_order_title,
                "asset": self.asset,
                "work_order_type": self.work_order_type,
                "priority": self.priority,
                "status": self.status,
                "total_cost": self.total_cost,
                "duration_days": self.duration_days
            },
            "insights": self.generate_work_order_insights(),
            "last_updated": now()
        }
        
        # Update or create Work Order Analytics DocType
        if frappe.db.exists("Work Order Analytics", self.work_order_id):
            work_order_analytics = frappe.get_doc("Work Order Analytics", self.work_order_id)
            work_order_analytics.update(analytics_data)
            work_order_analytics.save(ignore_permissions=True)
        else:
            work_order_analytics = frappe.new_doc("Work Order Analytics")
            work_order_analytics.update(analytics_data)
            work_order_analytics.name = self.work_order_id
            work_order_analytics.insert(ignore_permissions=True)

    def sync_work_order_data(self):
        """Sync work order data across systems"""
        # Sync with external maintenance systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_work_order_changes(self):
        """Process work order changes"""
        # Log changes
        self.log_work_order_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_work_order_changes(self):
        """Log work order changes"""
        frappe.get_doc({
            "doctype": "Work Order Change Log",
            "work_order": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Work Order {self.work_order_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update asset maintenance records
        self.update_asset_maintenance_records()

    def update_asset_maintenance_records(self):
        """Update asset maintenance records"""
        # Update asset maintenance summary
        frappe.db.sql("""
            UPDATE `tabAsset`
            SET last_maintenance_date = %s,
                total_maintenance_cost = (
                    SELECT SUM(total_cost) FROM `tabWork Order`
                    WHERE asset = %s AND status = 'Completed'
                )
            WHERE name = %s
        """, (self.work_order_date, self.asset, self.asset))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify maintenance team
        self.notify_maintenance_team()
        
        # Notify assigned technician
        self.notify_assigned_technician()

    def notify_maintenance_team(self):
        """Notify maintenance team"""
        frappe.get_doc({
            "doctype": "Work Order Notification",
            "work_order": self.name,
            "notification_type": "Work Order Update",
            "message": f"Work Order {self.work_order_id} has been updated",
            "recipients": "Maintenance Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_assigned_technician(self):
        """Notify assigned technician"""
        if self.assigned_technician:
            frappe.get_doc({
                "doctype": "Work Order Notification",
                "work_order": self.name,
                "notification_type": "Work Order Update",
                "message": f"Work Order {self.work_order_id} has been updated",
                "recipients": self.assigned_technician,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync work order data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_work_order_dashboard_data(self):
        """Get work order dashboard data"""
        return {
            "work_order_id": self.work_order_id,
            "work_order_title": self.work_order_title,
            "asset": self.asset,
            "work_order_type": self.work_order_type,
            "priority": self.priority,
            "status": self.status,
            "assigned_technician": self.assigned_technician,
            "scheduled_start_date": self.scheduled_start_date,
            "scheduled_end_date": self.scheduled_end_date,
            "duration_days": self.duration_days,
            "total_cost": self.total_cost,
            "total_labor_cost": self.total_labor_cost,
            "total_material_cost": self.total_material_cost,
            "insights": self.generate_work_order_insights()
        }

    @frappe.whitelist()
    def assign_technician(self, technician):
        """Assign technician to work order"""
        if self.status != "Open":
            frappe.throw(_("Only open work orders can be assigned"))
        
        self.assigned_technician = technician
        self.assigned_date = now()
        self.assigned_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Work Order {0} assigned to {1}").format(self.work_order_id, technician))
        return self.as_dict()

    @frappe.whitelist()
    def start_work_order(self):
        """Start work order"""
        if self.status != "Open":
            frappe.throw(_("Only open work orders can be started"))
        
        if not self.assigned_technician:
            frappe.throw(_("Work order must be assigned to a technician before starting"))
        
        self.status = "In Progress"
        self.actual_start_date = now()
        self.save()
        
        frappe.msgprint(_("Work Order {0} started").format(self.work_order_id))
        return self.as_dict()

    @frappe.whitelist()
    def complete_work_order(self):
        """Complete work order"""
        if self.status != "In Progress":
            frappe.throw(_("Only work orders in progress can be completed"))
        
        self.status = "Completed"
        self.actual_end_date = now()
        self.completed_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Work Order {0} completed").format(self.work_order_id))
        return self.as_dict()

    @frappe.whitelist()
    def cancel_work_order(self, reason=None):
        """Cancel work order"""
        if self.status == "Completed":
            frappe.throw(_("Completed work orders cannot be cancelled"))
        
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.cancelled_by = frappe.session.user
        self.cancellation_reason = reason
        self.save()
        
        frappe.msgprint(_("Work Order {0} cancelled").format(self.work_order_id))
        return self.as_dict()

    @frappe.whitelist()
    def add_labor_item(self, technician, hours, hourly_rate, description=None):
        """Add labor item to work order"""
        self.append("labor_items", {
            "technician": technician,
            "hours": hours,
            "hourly_rate": hourly_rate,
            "description": description
        })
        self.calculate_work_order_costs()
        self.save()
        
        frappe.msgprint(_("Labor item added to Work Order {0}").format(self.work_order_id))
        return self.as_dict()

    @frappe.whitelist()
    def add_material_item(self, material, quantity, unit_cost, description=None):
        """Add material item to work order"""
        self.append("material_items", {
            "material": material,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "description": description
        })
        self.calculate_work_order_costs()
        self.save()
        
        frappe.msgprint(_("Material item added to Work Order {0}").format(self.work_order_id))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_work_order(self):
        """Duplicate work order"""
        new_work_order = frappe.copy_doc(self)
        new_work_order.work_order_id = None
        new_work_order.status = "Open"
        new_work_order.work_order_date = now()
        new_work_order.assigned_technician = None
        new_work_order.assigned_date = None
        new_work_order.assigned_by = None
        new_work_order.save(ignore_permissions=True)
        
        frappe.msgprint(_("Work Order duplicated as {0}").format(new_work_order.work_order_id))
        return new_work_order.as_dict()
