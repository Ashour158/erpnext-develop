# KPI DocType - Complete KPI & OKR Management System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class KPI(Document):
    def autoname(self):
        """Generate unique KPI ID"""
        if not self.kpi_id:
            self.kpi_id = make_autoname("KPI-.YYYY.-.MM.-.#####")
        self.name = self.kpi_id

    def validate(self):
        """Validate KPI data"""
        self.validate_kpi_data()
        self.set_defaults()
        self.validate_employee_data()
        self.validate_kpi_period()
        self.calculate_kpi_score()

    def before_save(self):
        """Process before saving"""
        self.update_kpi_settings()
        self.generate_kpi_insights()
        self.calculate_performance_metrics()

    def after_insert(self):
        """Process after inserting new KPI"""
        self.create_kpi_entries()
        self.setup_kpi_workflow()

    def on_update(self):
        """Process on KPI update"""
        self.update_kpi_analytics()
        self.sync_kpi_data()
        self.process_kpi_changes()

    def validate_kpi_data(self):
        """Validate KPI information"""
        if not self.employee:
            frappe.throw(_("Employee is required"))
        
        if not self.kpi_name:
            frappe.throw(_("KPI name is required"))
        
        if not self.kpi_type:
            frappe.throw(_("KPI type is required"))
        
        if not self.target_value:
            frappe.throw(_("Target value is required"))

    def set_defaults(self):
        """Set default values for new KPI"""
        if not self.kpi_date:
            self.kpi_date = now()
        
        if not self.status:
            self.status = "Draft"
        
        if not self.assigned_by:
            self.assigned_by = frappe.session.user

    def validate_employee_data(self):
        """Validate employee information"""
        if not frappe.db.exists("Employee", self.employee):
            frappe.throw(_("Employee {0} does not exist").format(self.employee))

    def validate_kpi_period(self):
        """Validate KPI period"""
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                frappe.throw(_("Start date cannot be greater than end date"))

    def calculate_kpi_score(self):
        """Calculate KPI score"""
        if self.actual_value and self.target_value:
            # Calculate percentage achievement
            self.achievement_percentage = (self.actual_value / self.target_value) * 100
            
            # Calculate KPI score based on achievement
            if self.achievement_percentage >= 100:
                self.kpi_score = 100
            elif self.achievement_percentage >= 90:
                self.kpi_score = 90
            elif self.achievement_percentage >= 80:
                self.kpi_score = 80
            elif self.achievement_percentage >= 70:
                self.kpi_score = 70
            else:
                self.kpi_score = self.achievement_percentage
            
            # Determine performance level
            if self.kpi_score >= 90:
                self.performance_level = "Excellent"
            elif self.kpi_score >= 80:
                self.performance_level = "Good"
            elif self.kpi_score >= 70:
                self.performance_level = "Satisfactory"
            else:
                self.performance_level = "Needs Improvement"

    def calculate_performance_metrics(self):
        """Calculate performance metrics"""
        # Calculate trend analysis
        self.calculate_trend_analysis()
        
        # Calculate benchmark comparison
        self.calculate_benchmark_comparison()
        
        # Calculate improvement potential
        self.calculate_improvement_potential()

    def calculate_trend_analysis(self):
        """Calculate trend analysis"""
        # Get previous KPI data for trend analysis
        previous_kpis = frappe.get_list("KPI",
            filters={
                "employee": self.employee,
                "kpi_name": self.kpi_name,
                "status": "Completed",
                "end_date": ["<", self.start_date]
            },
            fields=["actual_value", "target_value", "kpi_score"],
            order_by="end_date desc",
            limit=3
        )
        
        if previous_kpis:
            # Calculate trend
            current_score = self.kpi_score
            previous_scores = [kpi.kpi_score for kpi in previous_kpis]
            average_previous_score = sum(previous_scores) / len(previous_scores)
            
            if current_score > average_previous_score:
                self.trend = "Improving"
            elif current_score < average_previous_score:
                self.trend = "Declining"
            else:
                self.trend = "Stable"
        else:
            self.trend = "New"

    def calculate_benchmark_comparison(self):
        """Calculate benchmark comparison"""
        # Get team/department average for comparison
        team_kpis = frappe.get_list("KPI",
            filters={
                "kpi_name": self.kpi_name,
                "status": "Completed",
                "end_date": ["between", [self.start_date, self.end_date]]
            },
            fields=["kpi_score"]
        )
        
        if team_kpis:
            team_scores = [kpi.kpi_score for kpi in team_kpis]
            team_average = sum(team_scores) / len(team_scores)
            
            if self.kpi_score > team_average:
                self.benchmark_comparison = "Above Average"
            elif self.kpi_score < team_average:
                self.benchmark_comparison = "Below Average"
            else:
                self.benchmark_comparison = "Average"
        else:
            self.benchmark_comparison = "No Data"

    def calculate_improvement_potential(self):
        """Calculate improvement potential"""
        if self.achievement_percentage < 100:
            self.improvement_potential = 100 - self.achievement_percentage
        else:
            self.improvement_potential = 0

    def create_kpi_entries(self):
        """Create KPI entries"""
        # Create KPI entry
        kpi_entry = frappe.new_doc("KPI Entry")
        kpi_entry.kpi = self.name
        kpi_entry.employee = self.employee
        kpi_entry.kpi_name = self.kpi_name
        kpi_entry.kpi_type = self.kpi_type
        kpi_entry.target_value = self.target_value
        kpi_entry.actual_value = self.actual_value
        kpi_entry.kpi_score = self.kpi_score
        kpi_entry.performance_level = self.performance_level
        kpi_entry.status = self.status
        kpi_entry.save(ignore_permissions=True)

    def setup_kpi_workflow(self):
        """Setup KPI workflow"""
        # Update KPI workflow status
        workflow_data = {
            "workflow_name": f"KPI Workflow - {self.kpi_id}",
            "workflow_type": "KPI",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create KPI Workflow DocType
        if frappe.db.exists("KPI Workflow", self.kpi_id):
            kpi_workflow = frappe.get_doc("KPI Workflow", self.kpi_id)
            kpi_workflow.update(workflow_data)
            kpi_workflow.save(ignore_permissions=True)
        else:
            kpi_workflow = frappe.new_doc("KPI Workflow")
            kpi_workflow.update(workflow_data)
            kpi_workflow.name = self.kpi_id
            kpi_workflow.insert(ignore_permissions=True)

    def update_kpi_settings(self):
        """Update KPI settings"""
        # Set KPI permissions
        self.set_kpi_permissions()
        
        # Update KPI workflow
        self.update_kpi_workflow()

    def set_kpi_permissions(self):
        """Set KPI permissions"""
        # Create KPI-specific roles
        kpi_roles = [
            f"KPI - {self.kpi_id}",
            f"Employee - {self.employee}",
            f"Type - {self.kpi_type}"
        ]
        
        # Ensure roles exist
        for role_name in kpi_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_kpi_workflow(self):
        """Update KPI workflow"""
        # Update KPI workflow status
        workflow_data = {
            "workflow_name": f"KPI Workflow - {self.kpi_id}",
            "workflow_type": "KPI",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create KPI Workflow DocType
        if frappe.db.exists("KPI Workflow", self.kpi_id):
            kpi_workflow = frappe.get_doc("KPI Workflow", self.kpi_id)
            kpi_workflow.update(workflow_data)
            kpi_workflow.save(ignore_permissions=True)
        else:
            kpi_workflow = frappe.new_doc("KPI Workflow")
            kpi_workflow.update(workflow_data)
            kpi_workflow.name = self.kpi_id
            kpi_workflow.insert(ignore_permissions=True)

    def generate_kpi_insights(self):
        """Generate KPI insights"""
        insights = {
            "kpi_id": self.kpi_id,
            "employee": self.employee,
            "kpi_name": self.kpi_name,
            "kpi_type": self.kpi_type,
            "target_value": self.target_value,
            "actual_value": self.actual_value,
            "achievement_percentage": self.achievement_percentage,
            "kpi_score": self.kpi_score,
            "performance_level": self.performance_level,
            "trend": self.trend,
            "benchmark_comparison": self.benchmark_comparison,
            "improvement_potential": self.improvement_potential,
            "recommendations": self.generate_recommendations()
        }
        
        self.kpi_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate KPI recommendations"""
        recommendations = []
        
        # Performance recommendations
        if self.performance_level == "Needs Improvement":
            recommendations.append("Focus on improving performance to meet targets")
        
        if self.achievement_percentage < 80:
            recommendations.append("Consider additional training or resources")
        
        # Trend recommendations
        if self.trend == "Declining":
            recommendations.append("Address declining performance trend")
        
        # Improvement recommendations
        if self.improvement_potential > 20:
            recommendations.append("Significant improvement potential identified")
        
        return recommendations

    def update_kpi_analytics(self):
        """Update KPI analytics"""
        # Update KPI analytics data
        analytics_data = {
            "analytics_name": f"KPI Analytics - {self.kpi_id}",
            "analytics_type": "KPI Analytics",
            "metrics": {
                "kpi_id": self.kpi_id,
                "employee": self.employee,
                "kpi_name": self.kpi_name,
                "kpi_score": self.kpi_score,
                "performance_level": self.performance_level,
                "trend": self.trend,
                "benchmark_comparison": self.benchmark_comparison
            },
            "insights": self.generate_kpi_insights(),
            "last_updated": now()
        }
        
        # Update or create KPI Analytics DocType
        if frappe.db.exists("KPI Analytics", self.kpi_id):
            kpi_analytics = frappe.get_doc("KPI Analytics", self.kpi_id)
            kpi_analytics.update(analytics_data)
            kpi_analytics.save(ignore_permissions=True)
        else:
            kpi_analytics = frappe.new_doc("KPI Analytics")
            kpi_analytics.update(analytics_data)
            kpi_analytics.name = self.kpi_id
            kpi_analytics.insert(ignore_permissions=True)

    def sync_kpi_data(self):
        """Sync KPI data across systems"""
        # Sync with external HR systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_kpi_changes(self):
        """Process KPI changes"""
        # Log changes
        self.log_kpi_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_kpi_changes(self):
        """Log KPI changes"""
        frappe.get_doc({
            "doctype": "KPI Change Log",
            "kpi": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"KPI {self.kpi_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update employee performance records
        self.update_employee_performance_records()

    def update_employee_performance_records(self):
        """Update employee performance records"""
        # Update employee performance summary
        frappe.db.sql("""
            UPDATE `tabEmployee`
            SET last_kpi_date = %s,
                average_kpi_score = (
                    SELECT AVG(kpi_score) FROM `tabKPI`
                    WHERE employee = %s AND status = 'Completed'
                )
            WHERE name = %s
        """, (self.end_date, self.employee, self.employee))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify HR team
        self.notify_hr_team()
        
        # Notify manager
        self.notify_manager()

    def notify_hr_team(self):
        """Notify HR team"""
        frappe.get_doc({
            "doctype": "KPI Notification",
            "kpi": self.name,
            "notification_type": "KPI Update",
            "message": f"KPI {self.kpi_id} has been updated",
            "recipients": "HR Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_manager(self):
        """Notify manager"""
        employee = frappe.get_doc("Employee", self.employee)
        if employee.reports_to:
            frappe.get_doc({
                "doctype": "KPI Notification",
                "kpi": self.name,
                "notification_type": "KPI Update",
                "message": f"KPI {self.kpi_id} has been updated",
                "recipients": employee.reports_to,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync KPI data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_kpi_dashboard_data(self):
        """Get KPI dashboard data"""
        return {
            "kpi_id": self.kpi_id,
            "employee": self.employee,
            "kpi_name": self.kpi_name,
            "kpi_type": self.kpi_type,
            "target_value": self.target_value,
            "actual_value": self.actual_value,
            "achievement_percentage": self.achievement_percentage,
            "kpi_score": self.kpi_score,
            "performance_level": self.performance_level,
            "trend": self.trend,
            "benchmark_comparison": self.benchmark_comparison,
            "improvement_potential": self.improvement_potential,
            "insights": self.generate_kpi_insights()
        }

    @frappe.whitelist()
    def update_actual_value(self, actual_value):
        """Update actual value and recalculate score"""
        self.actual_value = actual_value
        self.calculate_kpi_score()
        self.save()
        
        frappe.msgprint(_("KPI {0} updated with actual value {1}").format(self.kpi_id, actual_value))
        return self.as_dict()

    @frappe.whitelist()
    def complete_kpi(self):
        """Complete KPI"""
        if self.status != "Draft":
            frappe.throw(_("Only draft KPIs can be completed"))
        
        self.status = "Completed"
        self.completed_date = now()
        self.completed_by = frappe.session.user
        self.save()
        
        frappe.msgprint(_("KPI {0} completed").format(self.kpi_id))
        return self.as_dict()

    @frappe.whitelist()
    def approve_kpi(self):
        """Approve KPI"""
        if self.status != "Completed":
            frappe.throw(_("Only completed KPIs can be approved"))
        
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approved_date = now()
        self.save()
        
        frappe.msgprint(_("KPI {0} approved").format(self.kpi_id))
        return self.as_dict()

    @frappe.whitelist()
    def reject_kpi(self, reason=None):
        """Reject KPI"""
        if self.status != "Completed":
            frappe.throw(_("Only completed KPIs can be rejected"))
        
        self.status = "Rejected"
        self.rejected_by = frappe.session.user
        self.rejected_date = now()
        self.rejection_reason = reason
        self.save()
        
        frappe.msgprint(_("KPI {0} rejected").format(self.kpi_id))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_kpi(self):
        """Duplicate KPI"""
        new_kpi = frappe.copy_doc(self)
        new_kpi.kpi_id = None
        new_kpi.status = "Draft"
        new_kpi.kpi_date = now()
        new_kpi.actual_value = 0
        new_kpi.kpi_score = 0
        new_kpi.save(ignore_permissions=True)
        
        frappe.msgprint(_("KPI duplicated as {0}").format(new_kpi.kpi_id))
        return new_kpi.as_dict()
