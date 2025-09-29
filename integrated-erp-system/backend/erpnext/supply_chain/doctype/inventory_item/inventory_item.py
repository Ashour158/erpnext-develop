# Inventory Item DocType - Complete Inventory Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class InventoryItem(Document):
    def autoname(self):
        """Generate unique inventory item ID"""
        if not self.item_id:
            self.item_id = make_autoname("ITM-.YYYY.-.MM.-.#####")
        self.name = self.item_id

    def validate(self):
        """Validate inventory item data"""
        self.validate_item_data()
        self.set_defaults()
        self.validate_item_details()
        self.calculate_item_values()

    def before_save(self):
        """Process before saving"""
        self.update_item_settings()
        self.generate_item_insights()
        self.calculate_reorder_levels()

    def after_insert(self):
        """Process after inserting new item"""
        self.create_item_entries()
        self.setup_item_workflow()

    def on_update(self):
        """Process on item update"""
        self.update_item_analytics()
        self.sync_item_data()
        self.process_item_changes()

    def validate_item_data(self):
        """Validate item information"""
        if not self.item_name:
            frappe.throw(_("Item name is required"))
        
        if not self.item_type:
            frappe.throw(_("Item type is required"))
        
        if not self.unit_of_measure:
            frappe.throw(_("Unit of measure is required"))

    def set_defaults(self):
        """Set default values for new item"""
        if not self.item_date:
            self.item_date = now()
        
        if not self.status:
            self.status = "Active"
        
        if not self.item_type:
            self.item_type = "Stock"

    def validate_item_details(self):
        """Validate item details"""
        if self.serial_number:
            # Check for duplicate serial number
            existing_item = frappe.get_list("Inventory Item",
                filters={"serial_number": self.serial_number},
                fields=["name"]
            )
            
            if existing_item and existing_item[0].name != self.name:
                frappe.throw(_("Serial number {0} already exists").format(self.serial_number))

    def calculate_item_values(self):
        """Calculate item values"""
        # Calculate total value
        self.total_value = self.quantity_on_hand * self.unit_cost
        
        # Calculate reorder value
        self.reorder_value = self.reorder_level * self.unit_cost
        
        # Calculate average cost
        if self.quantity_on_hand > 0:
            self.average_cost = self.total_value / self.quantity_on_hand
        else:
            self.average_cost = 0

    def calculate_reorder_levels(self):
        """Calculate reorder levels"""
        if self.quantity_on_hand <= self.reorder_level:
            self.reorder_status = "Reorder Required"
        elif self.quantity_on_hand <= self.minimum_level:
            self.reorder_status = "Low Stock"
        else:
            self.reorder_status = "In Stock"

    def create_item_entries(self):
        """Create item entries"""
        # Create item entry
        item_entry = frappe.new_doc("Inventory Item Entry")
        item_entry.item = self.name
        item_entry.item_name = self.item_name
        item_entry.item_type = self.item_type
        item_entry.quantity_on_hand = self.quantity_on_hand
        item_entry.unit_cost = self.unit_cost
        item_entry.total_value = self.total_value
        item_entry.status = self.status
        item_entry.save(ignore_permissions=True)

    def setup_item_workflow(self):
        """Setup item workflow"""
        # Update item workflow status
        workflow_data = {
            "workflow_name": f"Inventory Item Workflow - {self.item_id}",
            "workflow_type": "Inventory Item",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Inventory Item Workflow DocType
        if frappe.db.exists("Inventory Item Workflow", self.item_id):
            item_workflow = frappe.get_doc("Inventory Item Workflow", self.item_id)
            item_workflow.update(workflow_data)
            item_workflow.save(ignore_permissions=True)
        else:
            item_workflow = frappe.new_doc("Inventory Item Workflow")
            item_workflow.update(workflow_data)
            item_workflow.name = self.item_id
            item_workflow.insert(ignore_permissions=True)

    def update_item_settings(self):
        """Update item settings"""
        # Set item permissions
        self.set_item_permissions()
        
        # Update item workflow
        self.update_item_workflow()

    def set_item_permissions(self):
        """Set item permissions"""
        # Create item-specific roles
        item_roles = [
            f"Inventory Item - {self.item_id}",
            f"Type - {self.item_type}",
            f"Status - {self.status}"
        ]
        
        # Ensure roles exist
        for role_name in item_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_item_workflow(self):
        """Update item workflow"""
        # Update item workflow status
        workflow_data = {
            "workflow_name": f"Inventory Item Workflow - {self.item_id}",
            "workflow_type": "Inventory Item",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Inventory Item Workflow DocType
        if frappe.db.exists("Inventory Item Workflow", self.item_id):
            item_workflow = frappe.get_doc("Inventory Item Workflow", self.item_id)
            item_workflow.update(workflow_data)
            item_workflow.save(ignore_permissions=True)
        else:
            item_workflow = frappe.new_doc("Inventory Item Workflow")
            item_workflow.update(workflow_data)
            item_workflow.name = self.item_id
            item_workflow.insert(ignore_permissions=True)

    def generate_item_insights(self):
        """Generate item insights"""
        insights = {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "item_type": self.item_type,
            "serial_number": self.serial_number,
            "quantity_on_hand": self.quantity_on_hand,
            "unit_cost": self.unit_cost,
            "total_value": self.total_value,
            "average_cost": self.average_cost,
            "reorder_level": self.reorder_level,
            "minimum_level": self.minimum_level,
            "reorder_status": self.reorder_status,
            "status": self.status,
            "location": self.location,
            "supplier": self.supplier,
            "recommendations": self.generate_recommendations()
        }
        
        self.item_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate item recommendations"""
        recommendations = []
        
        # Stock level recommendations
        if self.reorder_status == "Reorder Required":
            recommendations.append("Urgent reorder required - stock level critical")
        elif self.reorder_status == "Low Stock":
            recommendations.append("Consider reordering - stock level low")
        
        # Cost recommendations
        if self.unit_cost > 1000:
            recommendations.append("High-value item - consider security measures")
        
        # Location recommendations
        if not self.location:
            recommendations.append("Assign location for better inventory tracking")
        
        return recommendations

    def update_item_analytics(self):
        """Update item analytics"""
        # Update item analytics data
        analytics_data = {
            "analytics_name": f"Inventory Item Analytics - {self.item_id}",
            "analytics_type": "Inventory Item Analytics",
            "metrics": {
                "item_id": self.item_id,
                "item_name": self.item_name,
                "item_type": self.item_type,
                "quantity_on_hand": self.quantity_on_hand,
                "unit_cost": self.unit_cost,
                "total_value": self.total_value,
                "reorder_status": self.reorder_status,
                "status": self.status
            },
            "insights": self.generate_item_insights(),
            "last_updated": now()
        }
        
        # Update or create Inventory Item Analytics DocType
        if frappe.db.exists("Inventory Item Analytics", self.item_id):
            item_analytics = frappe.get_doc("Inventory Item Analytics", self.item_id)
            item_analytics.update(analytics_data)
            item_analytics.save(ignore_permissions=True)
        else:
            item_analytics = frappe.new_doc("Inventory Item Analytics")
            item_analytics.update(analytics_data)
            item_analytics.name = self.item_id
            item_analytics.insert(ignore_permissions=True)

    def sync_item_data(self):
        """Sync item data across systems"""
        # Sync with external inventory systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_item_changes(self):
        """Process item changes"""
        # Log changes
        self.log_item_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_item_changes(self):
        """Log item changes"""
        frappe.get_doc({
            "doctype": "Inventory Item Change Log",
            "item": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Inventory Item {self.item_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update supplier item records
        self.update_supplier_item_records()

    def update_supplier_item_records(self):
        """Update supplier item records"""
        if self.supplier:
            # Update supplier item summary
            frappe.db.sql("""
                UPDATE `tabSupplier`
                SET total_items = (
                    SELECT COUNT(*) FROM `tabInventory Item`
                    WHERE supplier = %s AND status = 'Active'
                )
                WHERE name = %s
            """, (self.supplier, self.supplier))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify inventory team
        self.notify_inventory_team()
        
        # Notify supplier
        self.notify_supplier()

    def notify_inventory_team(self):
        """Notify inventory team"""
        frappe.get_doc({
            "doctype": "Inventory Item Notification",
            "item": self.name,
            "notification_type": "Inventory Item Update",
            "message": f"Inventory Item {self.item_id} has been updated",
            "recipients": "Inventory Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_supplier(self):
        """Notify supplier"""
        if self.supplier:
            frappe.get_doc({
                "doctype": "Inventory Item Notification",
                "item": self.name,
                "notification_type": "Inventory Item Update",
                "message": f"Inventory Item {self.item_id} has been updated",
                "recipients": self.supplier,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync item data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_item_dashboard_data(self):
        """Get item dashboard data"""
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "item_type": self.item_type,
            "serial_number": self.serial_number,
            "quantity_on_hand": self.quantity_on_hand,
            "unit_cost": self.unit_cost,
            "total_value": self.total_value,
            "average_cost": self.average_cost,
            "reorder_level": self.reorder_level,
            "minimum_level": self.minimum_level,
            "reorder_status": self.reorder_status,
            "status": self.status,
            "location": self.location,
            "supplier": self.supplier,
            "insights": self.generate_item_insights()
        }

    @frappe.whitelist()
    def update_quantity(self, quantity_change, reason=None):
        """Update item quantity"""
        old_quantity = self.quantity_on_hand
        self.quantity_on_hand += quantity_change
        
        if self.quantity_on_hand < 0:
            frappe.throw(_("Quantity cannot be negative"))
        
        self.calculate_item_values()
        self.calculate_reorder_levels()
        self.save()
        
        # Log quantity change
        frappe.get_doc({
            "doctype": "Inventory Transaction",
            "item": self.name,
            "transaction_type": "Quantity Update",
            "quantity_change": quantity_change,
            "old_quantity": old_quantity,
            "new_quantity": self.quantity_on_hand,
            "reason": reason,
            "transaction_date": now()
        }).insert(ignore_permissions=True)
        
        frappe.msgprint(_("Item {0} quantity updated from {1} to {2}").format(
            self.item_id, old_quantity, self.quantity_on_hand
        ))
        return self.as_dict()

    @frappe.whitelist()
    def update_cost(self, new_cost, reason=None):
        """Update item cost"""
        old_cost = self.unit_cost
        self.unit_cost = new_cost
        self.calculate_item_values()
        self.save()
        
        # Log cost change
        frappe.get_doc({
            "doctype": "Inventory Transaction",
            "item": self.name,
            "transaction_type": "Cost Update",
            "old_cost": old_cost,
            "new_cost": new_cost,
            "reason": reason,
            "transaction_date": now()
        }).insert(ignore_permissions=True)
        
        frappe.msgprint(_("Item {0} cost updated from {1} to {2}").format(
            self.item_id, old_cost, new_cost
        ))
        return self.as_dict()

    @frappe.whitelist()
    def transfer_item(self, new_location, quantity=None):
        """Transfer item to new location"""
        if quantity and quantity > self.quantity_on_hand:
            frappe.throw(_("Transfer quantity cannot exceed available quantity"))
        
        transfer_quantity = quantity or self.quantity_on_hand
        old_location = self.location
        
        self.location = new_location
        if quantity:
            self.quantity_on_hand -= transfer_quantity
        
        self.save()
        
        # Log transfer
        frappe.get_doc({
            "doctype": "Inventory Transaction",
            "item": self.name,
            "transaction_type": "Transfer",
            "quantity_change": -transfer_quantity,
            "old_location": old_location,
            "new_location": new_location,
            "transaction_date": now()
        }).insert(ignore_permissions=True)
        
        frappe.msgprint(_("Item {0} transferred from {1} to {2}").format(
            self.item_id, old_location, new_location
        ))
        return self.as_dict()

    @frappe.whitelist()
    def set_reorder_level(self, new_level):
        """Set reorder level"""
        old_level = self.reorder_level
        self.reorder_level = new_level
        self.calculate_reorder_levels()
        self.save()
        
        frappe.msgprint(_("Item {0} reorder level updated from {1} to {2}").format(
            self.item_id, old_level, new_level
        ))
        return self.as_dict()

    @frappe.whitelist()
    def generate_reorder_report(self):
        """Generate reorder report"""
        if self.reorder_status == "Reorder Required":
            return {
                "item_id": self.item_id,
                "item_name": self.item_name,
                "current_quantity": self.quantity_on_hand,
                "reorder_level": self.reorder_level,
                "minimum_level": self.minimum_level,
                "reorder_quantity": self.reorder_level - self.quantity_on_hand,
                "unit_cost": self.unit_cost,
                "reorder_value": (self.reorder_level - self.quantity_on_hand) * self.unit_cost
            }
        else:
            return None

    @frappe.whitelist()
    def duplicate_item(self):
        """Duplicate item"""
        new_item = frappe.copy_doc(self)
        new_item.item_id = None
        new_item.serial_number = None
        new_item.status = "Draft"
        new_item.quantity_on_hand = 0
        new_item.total_value = 0
        new_item.save(ignore_permissions=True)
        
        frappe.msgprint(_("Item duplicated as {0}").format(new_item.item_id))
        return new_item.as_dict()
