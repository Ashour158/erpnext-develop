# Journal Entry DocType - Complete Journal Entry System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta

class JournalEntry(Document):
    def autoname(self):
        """Generate unique journal entry ID"""
        if not self.journal_entry_id:
            self.journal_entry_id = make_autoname("JE-.YYYY.-.MM.-.#####")
        self.name = self.journal_entry_id

    def validate(self):
        """Validate journal entry data"""
        self.validate_journal_entry_data()
        self.set_defaults()
        self.validate_accounts()
        self.validate_debit_credit_balance()

    def before_save(self):
        """Process before saving"""
        self.update_journal_entry_settings()
        self.generate_journal_entry_insights()

    def after_insert(self):
        """Process after inserting new journal entry"""
        self.create_gl_entries()
        self.setup_journal_entry_workflow()

    def on_update(self):
        """Process on journal entry update"""
        self.update_journal_entry_analytics()
        self.sync_journal_entry_data()
        self.process_journal_entry_changes()

    def validate_journal_entry_data(self):
        """Validate journal entry information"""
        if not self.posting_date:
            frappe.throw(_("Posting date is required"))
        
        if not self.company:
            frappe.throw(_("Company is required"))
        
        if not self.accounts:
            frappe.throw(_("At least one account entry is required"))

    def set_defaults(self):
        """Set default values for new journal entry"""
        if not self.posting_date:
            self.posting_date = now()
        
        if not self.status:
            self.status = "Draft"
        
        if not self.currency:
            self.currency = frappe.get_cached_value("Company", self.company, "default_currency")

    def validate_accounts(self):
        """Validate account entries"""
        for account in self.accounts:
            if not account.account:
                frappe.throw(_("Account is required for all entries"))
            
            if not frappe.db.exists("Account", account.account):
                frappe.throw(_("Account {0} does not exist").format(account.account))
            
            if not account.debit and not account.credit:
                frappe.throw(_("Either debit or credit amount is required"))
            
            if account.debit and account.credit:
                frappe.throw(_("Cannot have both debit and credit amounts"))

    def validate_debit_credit_balance(self):
        """Validate debit and credit balance"""
        total_debit = sum([flt(account.debit) for account in self.accounts])
        total_credit = sum([flt(account.credit) for account in self.accounts])
        
        if abs(total_debit - total_credit) > 0.01:
            frappe.throw(_("Total debit ({0}) must equal total credit ({1})").format(total_debit, total_credit))

    def create_gl_entries(self):
        """Create GL entries for journal entry"""
        for account in self.accounts:
            if account.debit or account.credit:
                gl_entry = frappe.new_doc("GL Entry")
                gl_entry.account = account.account
                gl_entry.debit = flt(account.debit)
                gl_entry.credit = flt(account.credit)
                gl_entry.party = account.party
                gl_entry.party_type = account.party_type
                gl_entry.against = account.against
                gl_entry.voucher_type = "Journal Entry"
                gl_entry.voucher_no = self.name
                gl_entry.posting_date = self.posting_date
                gl_entry.company = self.company
                gl_entry.remarks = self.remarks
                gl_entry.insert(ignore_permissions=True)

    def setup_journal_entry_workflow(self):
        """Setup journal entry workflow"""
        # Update journal entry workflow status
        workflow_data = {
            "workflow_name": f"Journal Entry Workflow - {self.journal_entry_id}",
            "workflow_type": "Journal Entry",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Post", "status": "Pending"}
            ]
        }
        
        # Update or create Journal Entry Workflow DocType
        if frappe.db.exists("Journal Entry Workflow", self.journal_entry_id):
            journal_workflow = frappe.get_doc("Journal Entry Workflow", self.journal_entry_id)
            journal_workflow.update(workflow_data)
            journal_workflow.save(ignore_permissions=True)
        else:
            journal_workflow = frappe.new_doc("Journal Entry Workflow")
            journal_workflow.update(workflow_data)
            journal_workflow.name = self.journal_entry_id
            journal_workflow.insert(ignore_permissions=True)

    def update_journal_entry_settings(self):
        """Update journal entry settings"""
        # Set journal entry permissions
        self.set_journal_entry_permissions()
        
        # Update journal entry workflow
        self.update_journal_entry_workflow()

    def set_journal_entry_permissions(self):
        """Set journal entry permissions"""
        # Create journal entry-specific roles
        journal_roles = [
            f"Journal Entry - {self.journal_entry_id}",
            f"Company - {self.company}",
            f"Type - {self.journal_entry_type}"
        ]
        
        # Ensure roles exist
        for role_name in journal_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_journal_entry_workflow(self):
        """Update journal entry workflow"""
        # Update journal entry workflow status
        workflow_data = {
            "workflow_name": f"Journal Entry Workflow - {self.journal_entry_id}",
            "workflow_type": "Journal Entry",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Post", "status": "Pending"}
            ]
        }
        
        # Update or create Journal Entry Workflow DocType
        if frappe.db.exists("Journal Entry Workflow", self.journal_entry_id):
            journal_workflow = frappe.get_doc("Journal Entry Workflow", self.journal_entry_id)
            journal_workflow.update(workflow_data)
            journal_workflow.save(ignore_permissions=True)
        else:
            journal_workflow = frappe.new_doc("Journal Entry Workflow")
            journal_workflow.update(workflow_data)
            journal_workflow.name = self.journal_entry_id
            journal_workflow.insert(ignore_permissions=True)

    def generate_journal_entry_insights(self):
        """Generate journal entry insights"""
        insights = {
            "journal_entry_id": self.journal_entry_id,
            "posting_date": self.posting_date,
            "company": self.company,
            "currency": self.currency,
            "status": self.status,
            "total_debit": sum([flt(account.debit) for account in self.accounts]),
            "total_credit": sum([flt(account.credit) for account in self.accounts]),
            "accounts_count": len(self.accounts),
            "recommendations": self.generate_recommendations()
        }
        
        self.journal_entry_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate journal entry recommendations"""
        recommendations = []
        
        # Balance recommendations
        total_debit = sum([flt(account.debit) for account in self.accounts])
        total_credit = sum([flt(account.credit) for account in self.accounts])
        
        if abs(total_debit - total_credit) > 0.01:
            recommendations.append("Ensure debit and credit amounts are balanced")
        
        # Account recommendations
        for account in self.accounts:
            if account.debit > 10000 or account.credit > 10000:
                recommendations.append(f"Large amount entry for account {account.account} - verify accuracy")
        
        return recommendations

    def update_journal_entry_analytics(self):
        """Update journal entry analytics"""
        # Update journal entry analytics data
        analytics_data = {
            "analytics_name": f"Journal Entry Analytics - {self.journal_entry_id}",
            "analytics_type": "Journal Entry Analytics",
            "metrics": {
                "journal_entry_id": self.journal_entry_id,
                "posting_date": self.posting_date,
                "company": self.company,
                "total_debit": sum([flt(account.debit) for account in self.accounts]),
                "total_credit": sum([flt(account.credit) for account in self.accounts]),
                "status": self.status
            },
            "insights": self.generate_journal_entry_insights(),
            "last_updated": now()
        }
        
        # Update or create Journal Entry Analytics DocType
        if frappe.db.exists("Journal Entry Analytics", self.journal_entry_id):
            journal_analytics = frappe.get_doc("Journal Entry Analytics", self.journal_entry_id)
            journal_analytics.update(analytics_data)
            journal_analytics.save(ignore_permissions=True)
        else:
            journal_analytics = frappe.new_doc("Journal Entry Analytics")
            journal_analytics.update(analytics_data)
            journal_analytics.name = self.journal_entry_id
            journal_analytics.insert(ignore_permissions=True)

    def sync_journal_entry_data(self):
        """Sync journal entry data across systems"""
        # Sync with external accounting systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_journal_entry_changes(self):
        """Process journal entry changes"""
        # Log changes
        self.log_journal_entry_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_journal_entry_changes(self):
        """Log journal entry changes"""
        frappe.get_doc({
            "doctype": "Journal Entry Change Log",
            "journal_entry": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Journal Entry {self.journal_entry_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update account balances
        self.update_account_balances()

    def update_account_balances(self):
        """Update account balances"""
        for account in self.accounts:
            if account.debit or account.credit:
                # Update account balance
                frappe.db.sql("""
                    UPDATE `tabAccount`
                    SET balance = balance + %s - %s
                    WHERE name = %s
                """, (flt(account.debit), flt(account.credit), account.account))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify finance team
        self.notify_finance_team()
        
        # Notify management
        self.notify_management()

    def notify_finance_team(self):
        """Notify finance team"""
        frappe.get_doc({
            "doctype": "Journal Entry Notification",
            "journal_entry": self.name,
            "notification_type": "Journal Entry Update",
            "message": f"Journal Entry {self.journal_entry_id} has been updated",
            "recipients": "Finance Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_management(self):
        """Notify management"""
        frappe.get_doc({
            "doctype": "Journal Entry Notification",
            "journal_entry": self.name,
            "notification_type": "Journal Entry Update",
            "message": f"Journal Entry {self.journal_entry_id} has been updated",
            "recipients": "Management",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync journal entry data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_journal_entry_dashboard_data(self):
        """Get journal entry dashboard data"""
        return {
            "journal_entry_id": self.journal_entry_id,
            "posting_date": self.posting_date,
            "company": self.company,
            "currency": self.currency,
            "status": self.status,
            "total_debit": sum([flt(account.debit) for account in self.accounts]),
            "total_credit": sum([flt(account.credit) for account in self.accounts]),
            "accounts_count": len(self.accounts),
            "insights": self.generate_journal_entry_insights()
        }

    @frappe.whitelist()
    def post_journal_entry(self):
        """Post journal entry"""
        if self.status != "Draft":
            frappe.throw(_("Only draft journal entries can be posted"))
        
        # Validate balance
        self.validate_debit_credit_balance()
        
        # Create GL entries
        self.create_gl_entries()
        
        # Update status
        self.status = "Posted"
        self.posted_date = now()
        self.posted_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Journal Entry {0} posted successfully").format(self.journal_entry_id))
        return self.as_dict()

    @frappe.whitelist()
    def cancel_journal_entry(self):
        """Cancel journal entry"""
        if self.status != "Posted":
            frappe.throw(_("Only posted journal entries can be cancelled"))
        
        # Reverse GL entries
        self.reverse_gl_entries()
        
        # Update status
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.cancelled_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("Journal Entry {0} cancelled successfully").format(self.journal_entry_id))
        return self.as_dict()

    def reverse_gl_entries(self):
        """Reverse GL entries for cancelled journal entry"""
        # Get existing GL entries
        gl_entries = frappe.get_list("GL Entry",
            filters={"voucher_no": self.name, "voucher_type": "Journal Entry"},
            fields=["name", "account", "debit", "credit"]
        )
        
        # Create reverse entries
        for entry in gl_entries:
            frappe.get_doc({
                "doctype": "GL Entry",
                "account": entry.account,
                "debit": entry.credit,
                "credit": entry.debit,
                "voucher_type": "Journal Entry",
                "voucher_no": self.name,
                "posting_date": now(),
                "company": self.company,
                "is_cancelled": 1
            }).insert(ignore_permissions=True)

    @frappe.whitelist()
    def duplicate_journal_entry(self):
        """Duplicate journal entry"""
        new_journal_entry = frappe.copy_doc(self)
        new_journal_entry.journal_entry_id = None
        new_journal_entry.status = "Draft"
        new_journal_entry.posting_date = now()
        new_journal_entry.save(ignore_permissions=True)
        
        frappe.msgprint(_("Journal Entry duplicated as {0}").format(new_journal_entry.journal_entry_id))
        return new_journal_entry.as_dict()

    @frappe.whitelist()
    def add_account_entry(self, account, debit=0, credit=0, party=None, party_type=None, against=None):
        """Add account entry to journal entry"""
        self.append("accounts", {
            "account": account,
            "debit": debit,
            "credit": credit,
            "party": party,
            "party_type": party_type,
            "against": against
        })
        
        self.save()
        frappe.msgprint(_("Account entry added to Journal Entry {0}").format(self.journal_entry_id))
        return self.as_dict()

    @frappe.whitelist()
    def remove_account_entry(self, account_name):
        """Remove account entry from journal entry"""
        for account in self.accounts:
            if account.name == account_name:
                self.remove(account)
                break
        
        self.save()
        frappe.msgprint(_("Account entry removed from Journal Entry {0}").format(self.journal_entry_id))
        return self.as_dict()
