# Purchase Order DocType - Complete Purchase Order Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class PurchaseOrder(Document):
    def autoname(self):
        """Generate unique purchase order ID"""
        if not self.purchase_order_id:
            self.purchase_order_id = make_autoname("PO-.YYYY.-.MM.-.#####")
        self.name = self.purchase_order_id

    def validate(self):
        """Validate purchase order data"""
        self.validate_purchase_order_data()
        self.set_defaults()
        self.validate_supplier_data()
        self.validate_items()
        self.calculate_totals()

    def before_save(self):
        """Process before saving"""
        self.update_purchase_order_settings()
        self.generate_purchase_order_insights()
        self.calculate_taxes()

    def after_insert(self):
        """Process after inserting new purchase order"""
        self.create_purchase_order_entries()
        self.setup_purchase_order_workflow()

    def on_update(self):
        """Process on purchase order update"""
        self.update_purchase_order_analytics()
        self.sync_purchase_order_data()
        self.process_purchase_order_changes()

    def validate_purchase_order_data(self):
        """Validate purchase order information"""
        if not self.supplier:
            frappe.throw(_("Supplier is required"))
        
        if not self.purchase_order_date:
            frappe.throw(_("Purchase order date is required"))
        
        if not self.delivery_date:
            frappe.throw(_("Delivery date is required"))

    def set_defaults(self):
        """Set default values for new purchase order"""
        if not self.purchase_order_date:
            self.purchase_order_date = now()
        
        if not self.delivery_date:
            self.delivery_date = add_days(self.purchase_order_date, 30)
        
        if not self.status:
            self.status = "Draft"
        
        if not self.currency:
            self.currency = frappe.get_cached_value("Company", self.company, "default_currency")

    def validate_supplier_data(self):
        """Validate supplier information"""
        if not frappe.db.exists("Supplier", self.supplier):
            frappe.throw(_("Supplier {0} does not exist").format(self.supplier))

    def validate_items(self):
        """Validate purchase order items"""
        if not self.items:
            frappe.throw(_("At least one item is required"))
        
        for item in self.items:
            if not item.item:
                frappe.throw(_("Item is required for all items"))
            
            if not item.qty or item.qty <= 0:
                frappe.throw(_("Quantity must be greater than 0"))
            
            if not item.rate or item.rate <= 0:
                frappe.throw(_("Rate must be greater than 0"))

    def calculate_totals(self):
        """Calculate purchase order totals"""
        self.total_qty = 0
        self.total_amount = 0
        self.total_tax = 0
        self.grand_total = 0

        for item in self.items:
            item.amount = item.qty * item.rate
            self.total_qty += item.qty
            self.total_amount += item.amount

        # Calculate taxes
        self.calculate_taxes()
        
        # Calculate grand total
        self.grand_total = self.total_amount + self.total_tax

    def calculate_taxes(self):
        """Calculate taxes and charges"""
        self.total_tax = 0
        
        for tax in self.taxes:
            if tax.tax_type == "Percentage":
                tax.tax_amount = (self.total_amount * tax.tax_rate) / 100
            elif tax.tax_type == "Fixed":
                tax.tax_amount = tax.tax_rate
            
            self.total_tax += tax.tax_amount

    def create_purchase_order_entries(self):
        """Create purchase order entries"""
        # Create purchase order entry
        po_entry = frappe.new_doc("Purchase Order Entry")
        po_entry.purchase_order = self.name
        po_entry.supplier = self.supplier
        po_entry.purchase_order_date = self.purchase_order_date
        po_entry.delivery_date = self.delivery_date
        po_entry.total_amount = self.total_amount
        po_entry.grand_total = self.grand_total
        po_entry.status = self.status
        po_entry.save(ignore_permissions=True)

    def setup_purchase_order_workflow(self):
        """Setup purchase order workflow"""
        # Update purchase order workflow status
        workflow_data = {
            "workflow_name": f"Purchase Order Workflow - {self.purchase_order_id}",
            "workflow_type": "Purchase Order",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Sent", "status": "Pending"},
                {"step": "Received", "status": "Pending"}
            ]
        }
        
        # Update or create Purchase Order Workflow DocType
        if frappe.db.exists("Purchase Order Workflow", self.purchase_order_id):
            po_workflow = frappe.get_doc("Purchase Order Workflow", self.purchase_order_id)
            po_workflow.update(workflow_data)
            po_workflow.save(ignore_permissions=True)
        else:
            po_workflow = frappe.new_doc("Purchase Order Workflow")
            po_workflow.update(workflow_data)
            po_workflow.name = self.purchase_order_id
            po_workflow.insert(ignore_permissions=True)

    def update_purchase_order_settings(self):
        """Update purchase order settings"""
        # Set purchase order permissions
        self.set_purchase_order_permissions()
        
        # Update purchase order workflow
        self.update_purchase_order_workflow()

    def set_purchase_order_permissions(self):
        """Set purchase order permissions"""
        # Create purchase order-specific roles
        po_roles = [
            f"Purchase Order - {self.purchase_order_id}",
            f"Supplier - {self.supplier}",
            f"Company - {self.company}"
        ]
        
        # Ensure roles exist
        for role_name in po_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_purchase_order_workflow(self):
        """Update purchase order workflow"""
        # Update purchase order workflow status
        workflow_data = {
            "workflow_name": f"Purchase Order Workflow - {self.purchase_order_id}",
            "workflow_type": "Purchase Order",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Sent", "status": "Pending"},
                {"step": "Received", "status": "Pending"}
            ]
        }
        
        # Update or create Purchase Order Workflow DocType
        if frappe.db.exists("Purchase Order Workflow", self.purchase_order_id):
            po_workflow = frappe.get_doc("Purchase Order Workflow", self.purchase_order_id)
            po_workflow.update(workflow_data)
            po_workflow.save(ignore_permissions=True)
        else:
            po_workflow = frappe.new_doc("Purchase Order Workflow")
            po_workflow.update(workflow_data)
            po_workflow.name = self.purchase_order_id
            po_workflow.insert(ignore_permissions=True)

    def generate_purchase_order_insights(self):
        """Generate purchase order insights"""
        insights = {
            "purchase_order_id": self.purchase_order_id,
            "supplier": self.supplier,
            "purchase_order_date": self.purchase_order_date,
            "delivery_date": self.delivery_date,
            "total_amount": self.total_amount,
            "grand_total": self.grand_total,
            "currency": self.currency,
            "status": self.status,
            "payment_terms": self.payment_terms,
            "items_count": len(self.items),
            "recommendations": self.generate_recommendations()
        }
        
        self.purchase_order_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate purchase order recommendations"""
        recommendations = []
        
        # Payment terms recommendations
        if self.payment_terms == "Net 30":
            recommendations.append("Consider negotiating better payment terms")
        
        # Supplier recommendations
        supplier = frappe.get_doc("Supplier", self.supplier)
        if supplier.rating < 3:
            recommendations.append("Consider alternative suppliers due to low rating")
        
        # Amount recommendations
        if self.grand_total > 100000:
            recommendations.append("Consider bulk discount negotiations")
        
        return recommendations

    def update_purchase_order_analytics(self):
        """Update purchase order analytics"""
        # Update purchase order analytics data
        analytics_data = {
            "analytics_name": f"Purchase Order Analytics - {self.purchase_order_id}",
            "analytics_type": "Purchase Order Analytics",
            "metrics": {
                "purchase_order_id": self.purchase_order_id,
                "supplier": self.supplier,
                "purchase_order_date": self.purchase_order_date,
                "delivery_date": self.delivery_date,
                "total_amount": self.total_amount,
                "grand_total": self.grand_total,
                "status": self.status
            },
            "insights": self.generate_purchase_order_insights(),
            "last_updated": now()
        }
        
        # Update or create Purchase Order Analytics DocType
        if frappe.db.exists("Purchase Order Analytics", self.purchase_order_id):
            po_analytics = frappe.get_doc("Purchase Order Analytics", self.purchase_order_id)
            po_analytics.update(analytics_data)
            po_analytics.save(ignore_permissions=True)
        else:
            po_analytics = frappe.new_doc("Purchase Order Analytics")
            po_analytics.update(analytics_data)
            po_analytics.name = self.purchase_order_id
            po_analytics.insert(ignore_permissions=True)

    def sync_purchase_order_data(self):
        """Sync purchase order data across systems"""
        # Sync with external procurement systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_purchase_order_changes(self):
        """Process purchase order changes"""
        # Log changes
        self.log_purchase_order_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_purchase_order_changes(self):
        """Log purchase order changes"""
        frappe.get_doc({
            "doctype": "Purchase Order Change Log",
            "purchase_order": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Purchase Order {self.purchase_order_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update supplier records
        self.update_supplier_records()

    def update_supplier_records(self):
        """Update supplier records"""
        # Update supplier outstanding
        frappe.db.sql("""
            UPDATE `tabSupplier`
            SET outstanding_amount = (
                SELECT SUM(grand_total) FROM `tabPurchase Order`
                WHERE supplier = %s AND status != 'Received'
            )
            WHERE name = %s
        """, (self.supplier, self.supplier))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify procurement team
        self.notify_procurement_team()
        
        # Notify supplier
        self.notify_supplier()

    def notify_procurement_team(self):
        """Notify procurement team"""
        frappe.get_doc({
            "doctype": "Purchase Order Notification",
            "purchase_order": self.name,
            "notification_type": "Purchase Order Update",
            "message": f"Purchase Order {self.purchase_order_id} has been updated",
            "recipients": "Procurement Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_supplier(self):
        """Notify supplier"""
        if self.supplier_email:
            frappe.get_doc({
                "doctype": "Purchase Order Notification",
                "purchase_order": self.name,
                "notification_type": "Purchase Order Update",
                "message": f"Purchase Order {self.purchase_order_id} has been updated",
                "recipients": self.supplier_email,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync purchase order data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_purchase_order_dashboard_data(self):
        """Get purchase order dashboard data"""
        return {
            "purchase_order_id": self.purchase_order_id,
            "supplier": self.supplier,
            "purchase_order_date": self.purchase_order_date,
            "delivery_date": self.delivery_date,
            "total_amount": self.total_amount,
            "grand_total": self.grand_total,
            "currency": self.currency,
            "status": self.status,
            "payment_terms": self.payment_terms,
            "items_count": len(self.items),
            "insights": self.generate_purchase_order_insights()
        }

    @frappe.whitelist()
    def send_purchase_order(self):
        """Send purchase order to supplier"""
        if not self.supplier_email:
            frappe.throw(_("Supplier email is required to send purchase order"))
        
        # Send email with purchase order PDF
        subject = f"Purchase Order {self.purchase_order_id} from {frappe.get_cached_value('Company', self.company, 'company_name')}"
        message = f"Please find attached purchase order {self.purchase_order_id} for your records."
        
        # Send email
        frappe.sendmail(
            recipients=self.supplier_email,
            subject=subject,
            content=message,
            attachments=[self.pdf_file] if self.pdf_generated else []
        )
        
        self.status = "Sent"
        self.sent_date = now()
        self.save()
        
        frappe.msgprint(_("Purchase Order {0} sent to {1}").format(self.purchase_order_id, self.supplier_email))
        return self.as_dict()

    @frappe.whitelist()
    def receive_purchase_order(self):
        """Receive purchase order"""
        if self.status != "Sent":
            frappe.throw(_("Only sent purchase orders can be received"))
        
        self.status = "Received"
        self.received_date = now()
        self.received_by = frappe.session.user
        self.save()
        
        # Update inventory
        self.update_inventory()
        
        frappe.msgprint(_("Purchase Order {0} received").format(self.purchase_order_id))
        return self.as_dict()

    def update_inventory(self):
        """Update inventory on receipt"""
        for item in self.items:
            # Update inventory item quantity
            frappe.db.sql("""
                UPDATE `tabInventory Item`
                SET quantity_on_hand = quantity_on_hand + %s,
                    total_value = (quantity_on_hand + %s) * unit_cost
                WHERE name = %s
            """, (item.qty, item.qty, item.item))

    @frappe.whitelist()
    def cancel_purchase_order(self):
        """Cancel purchase order"""
        if self.status == "Received":
            frappe.throw(_("Cannot cancel received purchase order"))
        
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.cancelled_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Purchase Order {0} cancelled").format(self.purchase_order_id))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_purchase_order(self):
        """Duplicate purchase order"""
        new_po = frappe.copy_doc(self)
        new_po.purchase_order_id = None
        new_po.status = "Draft"
        new_po.purchase_order_date = now()
        new_po.delivery_date = add_days(now(), 30)
        new_po.save(ignore_permissions=True)
        
        frappe.msgprint(_("Purchase Order duplicated as {0}").format(new_po.purchase_order_id))
        return new_po.as_dict()
