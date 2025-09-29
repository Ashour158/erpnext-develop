# Financial Statement DocType - Complete Financial Reporting System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class FinancialStatement(Document):
    def autoname(self):
        """Generate unique financial statement ID"""
        if not self.statement_id:
            self.statement_id = make_autoname("FS-.YYYY.-.MM.-.#####")
        self.name = self.statement_id

    def validate(self):
        """Validate financial statement data"""
        self.validate_statement_data()
        self.set_defaults()
        self.validate_period()
        self.calculate_totals()

    def before_save(self):
        """Process before saving"""
        self.update_statement_settings()
        self.generate_statement_insights()
        self.calculate_ratios()

    def after_insert(self):
        """Process after inserting new statement"""
        self.create_statement_entries()
        self.generate_statement_report()
        self.setup_statement_workflow()

    def on_update(self):
        """Process on statement update"""
        self.update_statement_analytics()
        self.sync_statement_data()
        self.process_statement_changes()

    def validate_statement_data(self):
        """Validate financial statement information"""
        if not self.statement_type:
            frappe.throw(_("Statement type is required"))
        
        if not self.company:
            frappe.throw(_("Company is required"))
        
        if not self.fiscal_year:
            frappe.throw(_("Fiscal year is required"))

    def set_defaults(self):
        """Set default values for new statement"""
        if not self.statement_date:
            self.statement_date = now()
        
        if not self.status:
            self.status = "Draft"
        
        if not self.currency:
            self.currency = frappe.get_cached_value("Company", self.company, "default_currency")

    def validate_period(self):
        """Validate statement period"""
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                frappe.throw(_("From date cannot be greater than to date"))

    def calculate_totals(self):
        """Calculate statement totals"""
        if self.statement_type == "Profit and Loss":
            self.calculate_pnl_totals()
        elif self.statement_type == "Balance Sheet":
            self.calculate_balance_sheet_totals()
        elif self.statement_type == "Cash Flow":
            self.calculate_cash_flow_totals()

    def calculate_pnl_totals(self):
        """Calculate Profit and Loss totals"""
        # Revenue totals
        self.total_revenue = sum([item.amount for item in self.revenue_items if item.amount])
        
        # Expense totals
        self.total_expenses = sum([item.amount for item in self.expense_items if item.amount])
        
        # Net profit/loss
        self.net_profit = self.total_revenue - self.total_expenses
        
        # Gross profit
        self.gross_profit = self.total_revenue - sum([item.amount for item in self.expense_items if item.expense_type == "Cost of Goods Sold"])

    def calculate_balance_sheet_totals(self):
        """Calculate Balance Sheet totals"""
        # Asset totals
        self.total_assets = sum([item.amount for item in self.asset_items if item.amount])
        
        # Liability totals
        self.total_liabilities = sum([item.amount for item in self.liability_items if item.amount])
        
        # Equity totals
        self.total_equity = sum([item.amount for item in self.equity_items if item.amount])
        
        # Balance check
        self.balance_check = self.total_assets - (self.total_liabilities + self.total_equity)

    def calculate_cash_flow_totals(self):
        """Calculate Cash Flow totals"""
        # Operating activities
        self.operating_cash_flow = sum([item.amount for item in self.operating_activities if item.amount])
        
        # Investing activities
        self.investing_cash_flow = sum([item.amount for item in self.investing_activities if item.amount])
        
        # Financing activities
        self.financing_cash_flow = sum([item.amount for item in self.financing_activities if item.amount])
        
        # Net cash flow
        self.net_cash_flow = self.operating_cash_flow + self.investing_cash_flow + self.financing_cash_flow

    def calculate_ratios(self):
        """Calculate financial ratios"""
        if self.statement_type == "Profit and Loss":
            # Profitability ratios
            self.gross_profit_margin = (self.gross_profit / self.total_revenue * 100) if self.total_revenue else 0
            self.net_profit_margin = (self.net_profit / self.total_revenue * 100) if self.total_revenue else 0
        
        elif self.statement_type == "Balance Sheet":
            # Liquidity ratios
            current_assets = sum([item.amount for item in self.asset_items if item.asset_type == "Current Assets"])
            current_liabilities = sum([item.amount for item in self.liability_items if item.liability_type == "Current Liabilities"])
            
            self.current_ratio = (current_assets / current_liabilities) if current_liabilities else 0
            self.quick_ratio = self.current_ratio  # Simplified calculation

    def create_statement_entries(self):
        """Create statement line items"""
        if self.statement_type == "Profit and Loss":
            self.create_pnl_entries()
        elif self.statement_type == "Balance Sheet":
            self.create_balance_sheet_entries()
        elif self.statement_type == "Cash Flow":
            self.create_cash_flow_entries()

    def create_pnl_entries(self):
        """Create Profit and Loss entries"""
        # Revenue entries
        revenue_accounts = frappe.get_list("Account", 
            filters={"account_type": "Income", "company": self.company},
            fields=["name", "account_name", "parent_account"]
        )
        
        for account in revenue_accounts:
            self.append("revenue_items", {
                "account": account.name,
                "account_name": account.account_name,
                "amount": self.get_account_balance(account.name),
                "revenue_type": "Operating Revenue"
            })

    def create_balance_sheet_entries(self):
        """Create Balance Sheet entries"""
        # Asset entries
        asset_accounts = frappe.get_list("Account",
            filters={"account_type": "Asset", "company": self.company},
            fields=["name", "account_name", "parent_account"]
        )
        
        for account in asset_accounts:
            self.append("asset_items", {
                "account": account.name,
                "account_name": account.account_name,
                "amount": self.get_account_balance(account.name),
                "asset_type": "Current Assets"
            })

    def create_cash_flow_entries(self):
        """Create Cash Flow entries"""
        # Operating activities
        self.append("operating_activities", {
            "activity": "Net Income",
            "amount": self.get_net_income(),
            "activity_type": "Operating"
        })

    def get_account_balance(self, account):
        """Get account balance for the period"""
        # Simplified balance calculation
        # In a real system, this would query the GL entries
        return frappe.db.sql("""
            SELECT COALESCE(SUM(debit - credit), 0) as balance
            FROM `tabGL Entry`
            WHERE account = %s
            AND posting_date BETWEEN %s AND %s
            AND docstatus = 1
        """, (account, self.from_date, self.to_date))[0][0] or 0

    def get_net_income(self):
        """Get net income for cash flow calculation"""
        # Get net income from P&L statement
        pnl_statement = frappe.get_doc("Financial Statement", {
            "statement_type": "Profit and Loss",
            "company": self.company,
            "fiscal_year": self.fiscal_year
        })
        return pnl_statement.net_profit or 0

    def generate_statement_report(self):
        """Generate statement report"""
        # Create PDF report
        report_data = {
            "statement_id": self.statement_id,
            "company": self.company,
            "statement_type": self.statement_type,
            "period": f"{self.from_date} to {self.to_date}",
            "currency": self.currency,
            "totals": self.get_statement_totals()
        }
        
        # Generate report file
        self.report_file = f"financial_statement_{self.statement_id}.pdf"
        self.report_generated = 1

    def get_statement_totals(self):
        """Get statement totals for reporting"""
        if self.statement_type == "Profit and Loss":
            return {
                "total_revenue": self.total_revenue,
                "total_expenses": self.total_expenses,
                "net_profit": self.net_profit,
                "gross_profit": self.gross_profit
            }
        elif self.statement_type == "Balance Sheet":
            return {
                "total_assets": self.total_assets,
                "total_liabilities": self.total_liabilities,
                "total_equity": self.total_equity,
                "balance_check": self.balance_check
            }
        elif self.statement_type == "Cash Flow":
            return {
                "operating_cash_flow": self.operating_cash_flow,
                "investing_cash_flow": self.investing_cash_flow,
                "financing_cash_flow": self.financing_cash_flow,
                "net_cash_flow": self.net_cash_flow
            }

    def update_statement_settings(self):
        """Update statement settings"""
        # Set statement permissions
        self.set_statement_permissions()
        
        # Update statement workflow
        self.update_statement_workflow()

    def set_statement_permissions(self):
        """Set statement permissions"""
        # Create statement-specific roles
        statement_roles = [
            f"Financial Statement - {self.statement_id}",
            f"Company - {self.company}",
            f"Type - {self.statement_type}"
        ]
        
        # Ensure roles exist
        for role_name in statement_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_statement_workflow(self):
        """Update statement workflow"""
        # Update statement workflow status
        workflow_data = {
            "workflow_name": f"Financial Statement Workflow - {self.statement_id}",
            "workflow_type": "Financial Statement",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Published", "status": "Pending"}
            ]
        }
        
        # Update or create Financial Statement Workflow DocType
        if frappe.db.exists("Financial Statement Workflow", self.statement_id):
            statement_workflow = frappe.get_doc("Financial Statement Workflow", self.statement_id)
            statement_workflow.update(workflow_data)
            statement_workflow.save(ignore_permissions=True)
        else:
            statement_workflow = frappe.new_doc("Financial Statement Workflow")
            statement_workflow.update(workflow_data)
            statement_workflow.name = self.statement_id
            statement_workflow.insert(ignore_permissions=True)

    def generate_statement_insights(self):
        """Generate statement insights"""
        insights = {
            "statement_type": self.statement_type,
            "company": self.company,
            "period": f"{self.from_date} to {self.to_date}",
            "totals": self.get_statement_totals(),
            "ratios": self.get_financial_ratios(),
            "trends": self.analyze_trends(),
            "recommendations": self.generate_recommendations()
        }
        
        self.statement_insights = json.dumps(insights)

    def get_financial_ratios(self):
        """Get financial ratios"""
        ratios = {}
        
        if self.statement_type == "Profit and Loss":
            ratios.update({
                "gross_profit_margin": self.gross_profit_margin,
                "net_profit_margin": self.net_profit_margin
            })
        elif self.statement_type == "Balance Sheet":
            ratios.update({
                "current_ratio": self.current_ratio,
                "quick_ratio": self.quick_ratio
            })
        
        return ratios

    def analyze_trends(self):
        """Analyze financial trends"""
        # Get previous period data for comparison
        previous_statement = frappe.get_doc("Financial Statement", {
            "statement_type": self.statement_type,
            "company": self.company,
            "fiscal_year": self.get_previous_fiscal_year()
        })
        
        trends = {}
        if previous_statement:
            current_totals = self.get_statement_totals()
            previous_totals = previous_statement.get_statement_totals()
            
            for key in current_totals:
                if key in previous_totals:
                    change = current_totals[key] - previous_totals[key]
                    percentage_change = (change / previous_totals[key] * 100) if previous_totals[key] else 0
                    trends[key] = {
                        "change": change,
                        "percentage_change": percentage_change
                    }
        
        return trends

    def generate_recommendations(self):
        """Generate financial recommendations"""
        recommendations = []
        
        if self.statement_type == "Profit and Loss":
            if self.net_profit_margin < 5:
                recommendations.append("Consider cost reduction strategies to improve profitability")
            
            if self.gross_profit_margin < 20:
                recommendations.append("Review pricing strategy or cost of goods sold")
        
        elif self.statement_type == "Balance Sheet":
            if self.current_ratio < 1:
                recommendations.append("Improve liquidity position to meet short-term obligations")
            
            if self.quick_ratio < 0.5:
                recommendations.append("Increase cash and liquid assets")
        
        return recommendations

    def get_previous_fiscal_year(self):
        """Get previous fiscal year"""
        current_year = int(self.fiscal_year.split("-")[0])
        return f"{current_year - 1}-{current_year}"

    def update_statement_analytics(self):
        """Update statement analytics"""
        # Update statement analytics data
        analytics_data = {
            "analytics_name": f"Financial Statement Analytics - {self.statement_id}",
            "analytics_type": "Financial Statement Analytics",
            "metrics": self.get_statement_totals(),
            "ratios": self.get_financial_ratios(),
            "insights": self.generate_statement_insights(),
            "last_updated": now()
        }
        
        # Update or create Financial Statement Analytics DocType
        if frappe.db.exists("Financial Statement Analytics", self.statement_id):
            statement_analytics = frappe.get_doc("Financial Statement Analytics", self.statement_id)
            statement_analytics.update(analytics_data)
            statement_analytics.save(ignore_permissions=True)
        else:
            statement_analytics = frappe.new_doc("Financial Statement Analytics")
            statement_analytics.update(analytics_data)
            statement_analytics.name = self.statement_id
            statement_analytics.insert(ignore_permissions=True)

    def sync_statement_data(self):
        """Sync statement data across systems"""
        # Sync with external accounting systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_statement_changes(self):
        """Process statement changes"""
        # Log changes
        self.log_statement_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_statement_changes(self):
        """Log statement changes"""
        frappe.get_doc({
            "doctype": "Financial Statement Change Log",
            "statement": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Financial Statement {self.statement_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update company financial records
        self.update_company_financial_records()

    def update_company_financial_records(self):
        """Update company financial records"""
        # Update company financial summary
        frappe.db.sql("""
            UPDATE `tabCompany`
            SET last_financial_statement = %s,
                last_statement_date = %s
            WHERE name = %s
        """, (self.statement_id, self.statement_date, self.company))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify finance team
        self.notify_finance_team()
        
        # Notify management
        self.notify_management()

    def notify_finance_team(self):
        """Notify finance team"""
        frappe.get_doc({
            "doctype": "Financial Statement Notification",
            "statement": self.name,
            "notification_type": "Statement Update",
            "message": f"Financial Statement {self.statement_id} has been updated",
            "recipients": "Finance Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_management(self):
        """Notify management"""
        frappe.get_doc({
            "doctype": "Financial Statement Notification",
            "statement": self.name,
            "notification_type": "Statement Update",
            "message": f"Financial Statement {self.statement_id} has been updated",
            "recipients": "Management",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync statement data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_statement_dashboard_data(self):
        """Get statement dashboard data"""
        return {
            "statement_id": self.statement_id,
            "statement_type": self.statement_type,
            "company": self.company,
            "fiscal_year": self.fiscal_year,
            "period": f"{self.from_date} to {self.to_date}",
            "currency": self.currency,
            "status": self.status,
            "totals": self.get_statement_totals(),
            "ratios": self.get_financial_ratios(),
            "insights": self.generate_statement_insights()
        }

    @frappe.whitelist()
    def approve_statement(self):
        """Approve financial statement"""
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approved_date = now()
        self.save()
        
        frappe.msgprint(_("Financial Statement {0} approved").format(self.statement_id))
        return self.as_dict()

    @frappe.whitelist()
    def publish_statement(self):
        """Publish financial statement"""
        if self.status != "Approved":
            frappe.throw(_("Statement must be approved before publishing"))
        
        self.status = "Published"
        self.published_date = now()
        self.save()
        
        frappe.msgprint(_("Financial Statement {0} published").format(self.statement_id))
        return self.as_dict()

    @frappe.whitelist()
    def export_statement(self, format="pdf"):
        """Export financial statement"""
        if format == "pdf":
            return self.generate_pdf_report()
        elif format == "excel":
            return self.generate_excel_report()
        elif format == "csv":
            return self.generate_csv_report()
        else:
            frappe.throw(_("Unsupported export format"))

    def generate_pdf_report(self):
        """Generate PDF report"""
        # Implementation for PDF generation
        return f"financial_statement_{self.statement_id}.pdf"

    def generate_excel_report(self):
        """Generate Excel report"""
        # Implementation for Excel generation
        return f"financial_statement_{self.statement_id}.xlsx"

    def generate_csv_report(self):
        """Generate CSV report"""
        # Implementation for CSV generation
        return f"financial_statement_{self.statement_id}.csv"
