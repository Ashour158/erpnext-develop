# Supplier DocType - Complete Supplier Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class Supplier(Document):
    def autoname(self):
        """Generate unique supplier ID"""
        if not self.supplier_id:
            self.supplier_id = make_autoname("SUP-.YYYY.-.MM.-.#####")
        self.name = self.supplier_id

    def validate(self):
        """Validate supplier data"""
        self.validate_supplier_data()
        self.set_defaults()
        self.validate_supplier_details()
        self.calculate_supplier_metrics()

    def before_save(self):
        """Process before saving"""
        self.update_supplier_settings()
        self.generate_supplier_insights()
        self.calculate_supplier_rating()

    def after_insert(self):
        """Process after inserting new supplier"""
        self.create_supplier_entries()
        self.setup_supplier_workflow()

    def on_update(self):
        """Process on supplier update"""
        self.update_supplier_analytics()
        self.sync_supplier_data()
        self.process_supplier_changes()

    def validate_supplier_data(self):
        """Validate supplier information"""
        if not self.supplier_name:
            frappe.throw(_("Supplier name is required"))
        
        if not self.supplier_type:
            frappe.throw(_("Supplier type is required"))
        
        if not self.contact_email:
            frappe.throw(_("Contact email is required"))

    def set_defaults(self):
        """Set default values for new supplier"""
        if not self.supplier_date:
            self.supplier_date = now()
        
        if not self.status:
            self.status = "Active"
        
        if not self.supplier_type:
            self.supplier_type = "Vendor"

    def validate_supplier_details(self):
        """Validate supplier details"""
        if self.contact_email:
            # Check for duplicate email
            existing_supplier = frappe.get_list("Supplier",
                filters={"contact_email": self.contact_email},
                fields=["name"]
            )
            
            if existing_supplier and existing_supplier[0].name != self.name:
                frappe.throw(_("Contact email {0} already exists").format(self.contact_email))

    def calculate_supplier_metrics(self):
        """Calculate supplier metrics"""
        # Calculate total orders
        self.total_orders = frappe.db.count("Purchase Order", {"supplier": self.name})
        
        # Calculate total value
        self.total_value = frappe.db.sql("""
            SELECT SUM(grand_total) FROM `tabPurchase Order`
            WHERE supplier = %s AND status = 'Received'
        """, (self.name,))[0][0] or 0
        
        # Calculate average order value
        if self.total_orders > 0:
            self.average_order_value = self.total_value / self.total_orders
        else:
            self.average_order_value = 0

    def calculate_supplier_rating(self):
        """Calculate supplier rating"""
        # Get supplier performance data
        performance_data = self.get_supplier_performance()
        
        # Calculate rating based on performance metrics
        rating = 0
        
        # On-time delivery (40% weight)
        if performance_data.get("on_time_delivery_rate", 0) >= 90:
            rating += 40
        elif performance_data.get("on_time_delivery_rate", 0) >= 80:
            rating += 30
        elif performance_data.get("on_time_delivery_rate", 0) >= 70:
            rating += 20
        else:
            rating += 10
        
        # Quality rating (30% weight)
        if performance_data.get("quality_rating", 0) >= 4:
            rating += 30
        elif performance_data.get("quality_rating", 0) >= 3:
            rating += 20
        elif performance_data.get("quality_rating", 0) >= 2:
            rating += 10
        else:
            rating += 5
        
        # Communication (20% weight)
        if performance_data.get("communication_rating", 0) >= 4:
            rating += 20
        elif performance_data.get("communication_rating", 0) >= 3:
            rating += 15
        elif performance_data.get("communication_rating", 0) >= 2:
            rating += 10
        else:
            rating += 5
        
        # Price competitiveness (10% weight)
        if performance_data.get("price_rating", 0) >= 4:
            rating += 10
        elif performance_data.get("price_rating", 0) >= 3:
            rating += 7
        elif performance_data.get("price_rating", 0) >= 2:
            rating += 5
        else:
            rating += 2
        
        self.rating = min(rating, 100)

    def get_supplier_performance(self):
        """Get supplier performance data"""
        # Get performance metrics from purchase orders
        performance_data = frappe.db.sql("""
            SELECT 
                AVG(on_time_delivery) as on_time_delivery_rate,
                AVG(quality_rating) as quality_rating,
                AVG(communication_rating) as communication_rating,
                AVG(price_rating) as price_rating
            FROM `tabPurchase Order`
            WHERE supplier = %s AND status = 'Received'
        """, (self.name,), as_dict=True)
        
        return performance_data[0] if performance_data else {}

    def create_supplier_entries(self):
        """Create supplier entries"""
        # Create supplier entry
        supplier_entry = frappe.new_doc("Supplier Entry")
        supplier_entry.supplier = self.name
        supplier_entry.supplier_name = self.supplier_name
        supplier_entry.supplier_type = self.supplier_type
        supplier_entry.contact_email = self.contact_email
        supplier_entry.contact_phone = self.contact_phone
        supplier_entry.status = self.status
        supplier_entry.save(ignore_permissions=True)

    def setup_supplier_workflow(self):
        """Setup supplier workflow"""
        # Update supplier workflow status
        workflow_data = {
            "workflow_name": f"Supplier Workflow - {self.supplier_id}",
            "workflow_type": "Supplier",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Supplier Workflow DocType
        if frappe.db.exists("Supplier Workflow", self.supplier_id):
            supplier_workflow = frappe.get_doc("Supplier Workflow", self.supplier_id)
            supplier_workflow.update(workflow_data)
            supplier_workflow.save(ignore_permissions=True)
        else:
            supplier_workflow = frappe.new_doc("Supplier Workflow")
            supplier_workflow.update(workflow_data)
            supplier_workflow.name = self.supplier_id
            supplier_workflow.insert(ignore_permissions=True)

    def update_supplier_settings(self):
        """Update supplier settings"""
        # Set supplier permissions
        self.set_supplier_permissions()
        
        # Update supplier workflow
        self.update_supplier_workflow()

    def set_supplier_permissions(self):
        """Set supplier permissions"""
        # Create supplier-specific roles
        supplier_roles = [
            f"Supplier - {self.supplier_id}",
            f"Type - {self.supplier_type}",
            f"Status - {self.status}"
        ]
        
        # Ensure roles exist
        for role_name in supplier_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_supplier_workflow(self):
        """Update supplier workflow"""
        # Update supplier workflow status
        workflow_data = {
            "workflow_name": f"Supplier Workflow - {self.supplier_id}",
            "workflow_type": "Supplier",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Supplier Workflow DocType
        if frappe.db.exists("Supplier Workflow", self.supplier_id):
            supplier_workflow = frappe.get_doc("Supplier Workflow", self.supplier_id)
            supplier_workflow.update(workflow_data)
            supplier_workflow.save(ignore_permissions=True)
        else:
            supplier_workflow = frappe.new_doc("Supplier Workflow")
            supplier_workflow.update(workflow_data)
            supplier_workflow.name = self.supplier_id
            supplier_workflow.insert(ignore_permissions=True)

    def generate_supplier_insights(self):
        """Generate supplier insights"""
        insights = {
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier_name,
            "supplier_type": self.supplier_type,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "status": self.status,
            "rating": self.rating,
            "total_orders": self.total_orders,
            "total_value": self.total_value,
            "average_order_value": self.average_order_value,
            "outstanding_amount": self.outstanding_amount,
            "payment_terms": self.payment_terms,
            "recommendations": self.generate_recommendations()
        }
        
        self.supplier_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate supplier recommendations"""
        recommendations = []
        
        # Rating recommendations
        if self.rating < 50:
            recommendations.append("Consider alternative suppliers due to low rating")
        elif self.rating < 70:
            recommendations.append("Monitor supplier performance closely")
        
        # Payment terms recommendations
        if self.payment_terms == "Net 30":
            recommendations.append("Consider negotiating better payment terms")
        
        # Order volume recommendations
        if self.total_orders < 5:
            recommendations.append("Increase order volume to build supplier relationship")
        
        return recommendations

    def update_supplier_analytics(self):
        """Update supplier analytics"""
        # Update supplier analytics data
        analytics_data = {
            "analytics_name": f"Supplier Analytics - {self.supplier_id}",
            "analytics_type": "Supplier Analytics",
            "metrics": {
                "supplier_id": self.supplier_id,
                "supplier_name": self.supplier_name,
                "supplier_type": self.supplier_type,
                "rating": self.rating,
                "total_orders": self.total_orders,
                "total_value": self.total_value,
                "average_order_value": self.average_order_value,
                "status": self.status
            },
            "insights": self.generate_supplier_insights(),
            "last_updated": now()
        }
        
        # Update or create Supplier Analytics DocType
        if frappe.db.exists("Supplier Analytics", self.supplier_id):
            supplier_analytics = frappe.get_doc("Supplier Analytics", self.supplier_id)
            supplier_analytics.update(analytics_data)
            supplier_analytics.save(ignore_permissions=True)
        else:
            supplier_analytics = frappe.new_doc("Supplier Analytics")
            supplier_analytics.update(analytics_data)
            supplier_analytics.name = self.supplier_id
            supplier_analytics.insert(ignore_permissions=True)

    def sync_supplier_data(self):
        """Sync supplier data across systems"""
        # Sync with external supplier systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_supplier_changes(self):
        """Process supplier changes"""
        # Log changes
        self.log_supplier_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_supplier_changes(self):
        """Log supplier changes"""
        frappe.get_doc({
            "doctype": "Supplier Change Log",
            "supplier": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Supplier {self.supplier_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update purchase order records
        self.update_purchase_order_records()

    def update_purchase_order_records(self):
        """Update purchase order records"""
        # Update purchase order supplier information
        frappe.db.sql("""
            UPDATE `tabPurchase Order`
            SET supplier_rating = %s,
                supplier_status = %s
            WHERE supplier = %s
        """, (self.rating, self.status, self.name))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify procurement team
        self.notify_procurement_team()
        
        # Notify supplier
        self.notify_supplier()

    def notify_procurement_team(self):
        """Notify procurement team"""
        frappe.get_doc({
            "doctype": "Supplier Notification",
            "supplier": self.name,
            "notification_type": "Supplier Update",
            "message": f"Supplier {self.supplier_id} has been updated",
            "recipients": "Procurement Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_supplier(self):
        """Notify supplier"""
        frappe.get_doc({
            "doctype": "Supplier Notification",
            "supplier": self.name,
            "notification_type": "Supplier Update",
            "message": f"Supplier {self.supplier_id} has been updated",
            "recipients": self.contact_email,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync supplier data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_supplier_dashboard_data(self):
        """Get supplier dashboard data"""
        return {
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier_name,
            "supplier_type": self.supplier_type,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "status": self.status,
            "rating": self.rating,
            "total_orders": self.total_orders,
            "total_value": self.total_value,
            "average_order_value": self.average_order_value,
            "outstanding_amount": self.outstanding_amount,
            "payment_terms": self.payment_terms,
            "insights": self.generate_supplier_insights()
        }

    @frappe.whitelist()
    def update_rating(self, new_rating, reason=None):
        """Update supplier rating"""
        old_rating = self.rating
        self.rating = new_rating
        self.rating_updated_date = now()
        self.rating_updated_by = frappe.session.user
        self.rating_reason = reason
        self.save()
        
        frappe.msgprint(_("Supplier {0} rating updated from {1} to {2}").format(
            self.supplier_id, old_rating, new_rating
        ))
        return self.as_dict()

    @frappe.whitelist()
    def update_payment_terms(self, new_terms):
        """Update payment terms"""
        old_terms = self.payment_terms
        self.payment_terms = new_terms
        self.save()
        
        frappe.msgprint(_("Supplier {0} payment terms updated from {1} to {2}").format(
            self.supplier_id, old_terms, new_terms
        ))
        return self.as_dict()

    @frappe.whitelist()
    def suspend_supplier(self, reason=None):
        """Suspend supplier"""
        if self.status == "Suspended":
            frappe.throw(_("Supplier is already suspended"))
        
        self.status = "Suspended"
        self.suspended_date = now()
        self.suspended_by = frappe.session.user
        self.suspension_reason = reason
        self.save()
        
        frappe.msgprint(_("Supplier {0} suspended").format(self.supplier_id))
        return self.as_dict()

    @frappe.whitelist()
    def reactivate_supplier(self):
        """Reactivate supplier"""
        if self.status != "Suspended":
            frappe.throw(_("Only suspended suppliers can be reactivated"))
        
        self.status = "Active"
        self.reactivated_date = now()
        self.reactivated_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Supplier {0} reactivated").format(self.supplier_id))
        return self.as_dict()

    @frappe.whitelist()
    def get_supplier_performance_report(self):
        """Get supplier performance report"""
        performance_data = self.get_supplier_performance()
        
        return {
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier_name,
            "rating": self.rating,
            "total_orders": self.total_orders,
            "total_value": self.total_value,
            "average_order_value": self.average_order_value,
            "on_time_delivery_rate": performance_data.get("on_time_delivery_rate", 0),
            "quality_rating": performance_data.get("quality_rating", 0),
            "communication_rating": performance_data.get("communication_rating", 0),
            "price_rating": performance_data.get("price_rating", 0)
        }

    @frappe.whitelist()
    def duplicate_supplier(self):
        """Duplicate supplier"""
        new_supplier = frappe.copy_doc(self)
        new_supplier.supplier_id = None
        new_supplier.contact_email = None
        new_supplier.status = "Draft"
        new_supplier.rating = 0
        new_supplier.total_orders = 0
        new_supplier.total_value = 0
        new_supplier.average_order_value = 0
        new_supplier.save(ignore_permissions=True)
        
        frappe.msgprint(_("Supplier duplicated as {0}").format(new_supplier.supplier_id))
        return new_supplier.as_dict()
