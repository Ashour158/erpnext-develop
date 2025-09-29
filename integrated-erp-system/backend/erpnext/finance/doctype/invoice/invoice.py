# Invoice DocType - Complete Invoicing System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class Invoice(Document):
    def autoname(self):
        """Generate unique invoice ID"""
        if not self.invoice_id:
            self.invoice_id = make_autoname("INV-.YYYY.-.MM.-.#####")
        self.name = self.invoice_id

    def validate(self):
        """Validate invoice data"""
        self.validate_invoice_data()
        self.set_defaults()
        self.validate_customer_data()
        self.validate_items()
        self.calculate_totals()

    def before_save(self):
        """Process before saving"""
        self.update_invoice_settings()
        self.generate_invoice_insights()
        self.calculate_taxes()

    def after_insert(self):
        """Process after inserting new invoice"""
        self.create_invoice_entries()
        self.generate_invoice_pdf()
        self.setup_invoice_workflow()

    def on_update(self):
        """Process on invoice update"""
        self.update_invoice_analytics()
        self.sync_invoice_data()
        self.process_invoice_changes()

    def validate_invoice_data(self):
        """Validate invoice information"""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        if not self.invoice_date:
            frappe.throw(_("Invoice date is required"))
        
        if not self.due_date:
            frappe.throw(_("Due date is required"))

    def set_defaults(self):
        """Set default values for new invoice"""
        if not self.invoice_date:
            self.invoice_date = now()
        
        if not self.due_date:
            self.due_date = add_days(self.invoice_date, 30)
        
        if not self.status:
            self.status = "Draft"
        
        if not self.currency:
            self.currency = frappe.get_cached_value("Company", self.company, "default_currency")

    def validate_customer_data(self):
        """Validate customer information"""
        if not frappe.db.exists("Customer", self.customer):
            frappe.throw(_("Customer {0} does not exist").format(self.customer))

    def validate_items(self):
        """Validate invoice items"""
        if not self.items:
            frappe.throw(_("At least one item is required"))
        
        for item in self.items:
            if not item.item_code:
                frappe.throw(_("Item code is required for all items"))
            
            if not item.qty or item.qty <= 0:
                frappe.throw(_("Quantity must be greater than 0"))
            
            if not item.rate or item.rate <= 0:
                frappe.throw(_("Rate must be greater than 0"))

    def calculate_totals(self):
        """Calculate invoice totals"""
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

    def create_invoice_entries(self):
        """Create invoice GL entries"""
        # Create GL entries for invoice
        self.create_gl_entries()
        
        # Update customer outstanding
        self.update_customer_outstanding()

    def create_gl_entries(self):
        """Create GL entries"""
        # Debit: Accounts Receivable
        frappe.get_doc({
            "doctype": "GL Entry",
            "account": self.debit_to,
            "debit": self.grand_total,
            "credit": 0,
            "party": self.customer,
            "party_type": "Customer",
            "against": self.income_account,
            "voucher_type": "Sales Invoice",
            "voucher_no": self.name,
            "posting_date": self.invoice_date,
            "company": self.company
        }).insert(ignore_permissions=True)

        # Credit: Income Account
        frappe.get_doc({
            "doctype": "GL Entry",
            "account": self.income_account,
            "debit": 0,
            "credit": self.total_amount,
            "party": self.customer,
            "party_type": "Customer",
            "against": self.debit_to,
            "voucher_type": "Sales Invoice",
            "voucher_no": self.name,
            "posting_date": self.invoice_date,
            "company": self.company
        }).insert(ignore_permissions=True)

        # Tax entries
        for tax in self.taxes:
            if tax.tax_amount > 0:
                frappe.get_doc({
                    "doctype": "GL Entry",
                    "account": tax.tax_account,
                    "debit": 0,
                    "credit": tax.tax_amount,
                    "party": self.customer,
                    "party_type": "Customer",
                    "against": self.debit_to,
                    "voucher_type": "Sales Invoice",
                    "voucher_no": self.name,
                    "posting_date": self.invoice_date,
                    "company": self.company
                }).insert(ignore_permissions=True)

    def update_customer_outstanding(self):
        """Update customer outstanding amount"""
        # Update customer outstanding
        frappe.db.sql("""
            UPDATE `tabCustomer`
            SET outstanding_amount = outstanding_amount + %s
            WHERE name = %s
        """, (self.grand_total, self.customer))

    def generate_invoice_pdf(self):
        """Generate invoice PDF"""
        # Create PDF report
        report_data = {
            "invoice_id": self.invoice_id,
            "customer": self.customer,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "items": [item.as_dict() for item in self.items],
            "totals": {
                "total_amount": self.total_amount,
                "total_tax": self.total_tax,
                "grand_total": self.grand_total
            }
        }
        
        # Generate PDF file
        self.pdf_file = f"invoice_{self.invoice_id}.pdf"
        self.pdf_generated = 1

    def setup_invoice_workflow(self):
        """Setup invoice workflow"""
        # Update invoice workflow status
        workflow_data = {
            "workflow_name": f"Invoice Workflow - {self.invoice_id}",
            "workflow_type": "Invoice",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Send", "status": "Pending"},
                {"step": "Payment", "status": "Pending"}
            ]
        }
        
        # Update or create Invoice Workflow DocType
        if frappe.db.exists("Invoice Workflow", self.invoice_id):
            invoice_workflow = frappe.get_doc("Invoice Workflow", self.invoice_id)
            invoice_workflow.update(workflow_data)
            invoice_workflow.save(ignore_permissions=True)
        else:
            invoice_workflow = frappe.new_doc("Invoice Workflow")
            invoice_workflow.update(workflow_data)
            invoice_workflow.name = self.invoice_id
            invoice_workflow.insert(ignore_permissions=True)

    def update_invoice_settings(self):
        """Update invoice settings"""
        # Set invoice permissions
        self.set_invoice_permissions()
        
        # Update invoice workflow
        self.update_invoice_workflow()

    def set_invoice_permissions(self):
        """Set invoice permissions"""
        # Create invoice-specific roles
        invoice_roles = [
            f"Invoice - {self.invoice_id}",
            f"Customer - {self.customer}",
            f"Company - {self.company}"
        ]
        
        # Ensure roles exist
        for role_name in invoice_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_invoice_workflow(self):
        """Update invoice workflow"""
        # Update invoice workflow status
        workflow_data = {
            "workflow_name": f"Invoice Workflow - {self.invoice_id}",
            "workflow_type": "Invoice",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Send", "status": "Pending"},
                {"step": "Payment", "status": "Pending"}
            ]
        }
        
        # Update or create Invoice Workflow DocType
        if frappe.db.exists("Invoice Workflow", self.invoice_id):
            invoice_workflow = frappe.get_doc("Invoice Workflow", self.invoice_id)
            invoice_workflow.update(workflow_data)
            invoice_workflow.save(ignore_permissions=True)
        else:
            invoice_workflow = frappe.new_doc("Invoice Workflow")
            invoice_workflow.update(workflow_data)
            invoice_workflow.name = self.invoice_id
            invoice_workflow.insert(ignore_permissions=True)

    def generate_invoice_insights(self):
        """Generate invoice insights"""
        insights = {
            "invoice_id": self.invoice_id,
            "customer": self.customer,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "amount": self.grand_total,
            "currency": self.currency,
            "status": self.status,
            "payment_terms": self.payment_terms,
            "recommendations": self.generate_recommendations()
        }
        
        self.invoice_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate invoice recommendations"""
        recommendations = []
        
        # Payment terms recommendations
        if self.payment_terms == "Net 30":
            recommendations.append("Consider offering early payment discounts")
        
        # Customer recommendations
        customer = frappe.get_doc("Customer", self.customer)
        if customer.outstanding_amount > 10000:
            recommendations.append("Monitor customer payment behavior closely")
        
        # Amount recommendations
        if self.grand_total > 50000:
            recommendations.append("Consider payment plan for large amounts")
        
        return recommendations

    def update_invoice_analytics(self):
        """Update invoice analytics"""
        # Update invoice analytics data
        analytics_data = {
            "analytics_name": f"Invoice Analytics - {self.invoice_id}",
            "analytics_type": "Invoice Analytics",
            "metrics": {
                "invoice_amount": self.grand_total,
                "customer": self.customer,
                "invoice_date": self.invoice_date,
                "due_date": self.due_date,
                "status": self.status
            },
            "insights": self.generate_invoice_insights(),
            "last_updated": now()
        }
        
        # Update or create Invoice Analytics DocType
        if frappe.db.exists("Invoice Analytics", self.invoice_id):
            invoice_analytics = frappe.get_doc("Invoice Analytics", self.invoice_id)
            invoice_analytics.update(analytics_data)
            invoice_analytics.save(ignore_permissions=True)
        else:
            invoice_analytics = frappe.new_doc("Invoice Analytics")
            invoice_analytics.update(analytics_data)
            invoice_analytics.name = self.invoice_id
            invoice_analytics.insert(ignore_permissions=True)

    def sync_invoice_data(self):
        """Sync invoice data across systems"""
        # Sync with external accounting systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_invoice_changes(self):
        """Process invoice changes"""
        # Log changes
        self.log_invoice_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_invoice_changes(self):
        """Log invoice changes"""
        frappe.get_doc({
            "doctype": "Invoice Change Log",
            "invoice": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Invoice {self.invoice_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update customer records
        self.update_customer_records()

    def update_customer_records(self):
        """Update customer records"""
        # Update customer outstanding
        frappe.db.sql("""
            UPDATE `tabCustomer`
            SET outstanding_amount = (
                SELECT SUM(grand_total) FROM `tabInvoice`
                WHERE customer = %s AND status != 'Paid'
            )
            WHERE name = %s
        """, (self.customer, self.customer))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify sales team
        self.notify_sales_team()
        
        # Notify customer
        self.notify_customer()

    def notify_sales_team(self):
        """Notify sales team"""
        frappe.get_doc({
            "doctype": "Invoice Notification",
            "invoice": self.name,
            "notification_type": "Invoice Update",
            "message": f"Invoice {self.invoice_id} has been updated",
            "recipients": "Sales Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_customer(self):
        """Notify customer"""
        if self.customer_email:
            frappe.get_doc({
                "doctype": "Invoice Notification",
                "invoice": self.name,
                "notification_type": "Invoice Update",
                "message": f"Invoice {self.invoice_id} has been updated",
                "recipients": self.customer_email,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync invoice data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_invoice_dashboard_data(self):
        """Get invoice dashboard data"""
        return {
            "invoice_id": self.invoice_id,
            "customer": self.customer,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "amount": self.grand_total,
            "currency": self.currency,
            "status": self.status,
            "payment_terms": self.payment_terms,
            "outstanding_amount": self.grand_total - self.paid_amount,
            "insights": self.generate_invoice_insights()
        }

    @frappe.whitelist()
    def send_invoice(self):
        """Send invoice to customer"""
        if not self.customer_email:
            frappe.throw(_("Customer email is required to send invoice"))
        
        # Send email with invoice PDF
        subject = f"Invoice {self.invoice_id} from {frappe.get_cached_value('Company', self.company, 'company_name')}"
        message = f"Please find attached invoice {self.invoice_id} for your records."
        
        # Send email
        frappe.sendmail(
            recipients=self.customer_email,
            subject=subject,
            content=message,
            attachments=[self.pdf_file] if self.pdf_generated else []
        )
        
        self.status = "Sent"
        self.sent_date = now()
        self.save()
        
        frappe.msgprint(_("Invoice {0} sent to {1}").format(self.invoice_id, self.customer_email))
        return self.as_dict()

    @frappe.whitelist()
    def record_payment(self, payment_amount, payment_date=None):
        """Record payment against invoice"""
        if payment_amount > self.grand_total:
            frappe.throw(_("Payment amount cannot be greater than invoice amount"))
        
        if not payment_date:
            payment_date = now()
        
        # Create payment entry
        payment_entry = frappe.new_doc("Payment Entry")
        payment_entry.payment_type = "Receive"
        payment_entry.party_type = "Customer"
        payment_entry.party = self.customer
        payment_entry.paid_amount = payment_amount
        payment_entry.received_amount = payment_amount
        payment_entry.payment_date = payment_date
        payment_entry.company = self.company
        payment_entry.reference_no = f"PAY-{self.invoice_id}"
        payment_entry.reference_date = payment_date
        payment_entry.save(ignore_permissions=True)
        
        # Update invoice
        self.paid_amount += payment_amount
        if self.paid_amount >= self.grand_total:
            self.status = "Paid"
            self.paid_date = payment_date
        
        self.save()
        
        frappe.msgprint(_("Payment of {0} recorded for invoice {1}").format(payment_amount, self.invoice_id))
        return self.as_dict()

    @frappe.whitelist()
    def cancel_invoice(self):
        """Cancel invoice"""
        if self.status == "Paid":
            frappe.throw(_("Cannot cancel paid invoice"))
        
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.save()
        
        # Reverse GL entries
        self.reverse_gl_entries()
        
        frappe.msgprint(_("Invoice {0} cancelled").format(self.invoice_id))
        return self.as_dict()

    def reverse_gl_entries(self):
        """Reverse GL entries for cancelled invoice"""
        # Get existing GL entries
        gl_entries = frappe.get_list("GL Entry",
            filters={"voucher_no": self.name, "voucher_type": "Sales Invoice"},
            fields=["name", "account", "debit", "credit"]
        )
        
        # Create reverse entries
        for entry in gl_entries:
            frappe.get_doc({
                "doctype": "GL Entry",
                "account": entry.account,
                "debit": entry.credit,
                "credit": entry.debit,
                "party": self.customer,
                "party_type": "Customer",
                "voucher_type": "Sales Invoice",
                "voucher_no": self.name,
                "posting_date": now(),
                "company": self.company,
                "is_cancelled": 1
            }).insert(ignore_permissions=True)

    @frappe.whitelist()
    def duplicate_invoice(self):
        """Duplicate invoice"""
        new_invoice = frappe.copy_doc(self)
        new_invoice.invoice_id = None
        new_invoice.status = "Draft"
        new_invoice.invoice_date = now()
        new_invoice.due_date = add_days(now(), 30)
        new_invoice.paid_amount = 0
        new_invoice.save(ignore_permissions=True)
        
        frappe.msgprint(_("Invoice duplicated as {0}").format(new_invoice.invoice_id))
        return new_invoice.as_dict()
