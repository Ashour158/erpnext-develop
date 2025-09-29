# Attendance DocType - Complete Attendance Management System with Geolocation

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt, time_diff_in_hours
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import math

class Attendance(Document):
    def autoname(self):
        """Generate unique attendance ID"""
        if not self.attendance_id:
            self.attendance_id = make_autoname("ATT-.YYYY.-.MM.-.#####")
        self.name = self.attendance_id

    def validate(self):
        """Validate attendance data"""
        self.validate_attendance_data()
        self.set_defaults()
        self.validate_employee_data()
        self.validate_attendance_period()
        self.calculate_working_hours()

    def before_save(self):
        """Process before saving"""
        self.update_attendance_settings()
        self.generate_attendance_insights()
        self.validate_geolocation()

    def after_insert(self):
        """Process after inserting new attendance"""
        self.create_attendance_entries()
        self.setup_attendance_workflow()

    def on_update(self):
        """Process on attendance update"""
        self.update_attendance_analytics()
        self.sync_attendance_data()
        self.process_attendance_changes()

    def validate_attendance_data(self):
        """Validate attendance information"""
        if not self.employee:
            frappe.throw(_("Employee is required"))
        
        if not self.attendance_date:
            frappe.throw(_("Attendance date is required"))
        
        if not self.check_in_time:
            frappe.throw(_("Check-in time is required"))

    def set_defaults(self):
        """Set default values for new attendance"""
        if not self.attendance_date:
            self.attendance_date = now().date()
        
        if not self.status:
            self.status = "Present"
        
        if not self.attendance_type:
            self.attendance_type = "Regular"

    def validate_employee_data(self):
        """Validate employee information"""
        if not frappe.db.exists("Employee", self.employee):
            frappe.throw(_("Employee {0} does not exist").format(self.employee))

    def validate_attendance_period(self):
        """Validate attendance period"""
        if self.check_in_time and self.check_out_time:
            if self.check_in_time > self.check_out_time:
                frappe.throw(_("Check-in time cannot be greater than check-out time"))

    def calculate_working_hours(self):
        """Calculate working hours"""
        if self.check_in_time and self.check_out_time:
            # Calculate total working hours
            self.working_hours = time_diff_in_hours(self.check_out_time, self.check_in_time)
            
            # Calculate break hours
            if self.break_start_time and self.break_end_time:
                self.break_hours = time_diff_in_hours(self.break_end_time, self.break_start_time)
            else:
                self.break_hours = 0
            
            # Calculate net working hours
            self.net_working_hours = self.working_hours - self.break_hours
            
            # Calculate overtime hours
            standard_hours = 8  # Standard working hours per day
            if self.net_working_hours > standard_hours:
                self.overtime_hours = self.net_working_hours - standard_hours
            else:
                self.overtime_hours = 0

    def validate_geolocation(self):
        """Validate geolocation data"""
        if self.check_in_latitude and self.check_in_longitude:
            # Validate check-in location
            self.validate_location(self.check_in_latitude, self.check_in_longitude, "check-in")
        
        if self.check_out_latitude and self.check_out_longitude:
            # Validate check-out location
            self.validate_location(self.check_out_latitude, self.check_out_longitude, "check-out")

    def validate_location(self, latitude, longitude, location_type):
        """Validate employee location"""
        # Get employee's assigned office location
        employee = frappe.get_doc("Employee", self.employee)
        if employee.office_location:
            office_location = frappe.get_doc("Office Location", employee.office_location)
            
            # Calculate distance between employee location and office
            distance = self.calculate_distance(
                latitude, longitude,
                office_location.latitude, office_location.longitude
            )
            
            # Check if employee is within allowed radius (default: 100 meters)
            allowed_radius = office_location.allowed_radius or 100
            
            if distance > allowed_radius:
                frappe.throw(_("Employee is not within allowed radius for {0}. Distance: {1}m, Allowed: {2}m").format(
                    location_type, round(distance), allowed_radius
                ))

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in meters
        r = 6371000
        return c * r

    def create_attendance_entries(self):
        """Create attendance entries"""
        # Create attendance entry
        attendance_entry = frappe.new_doc("Attendance Entry")
        attendance_entry.attendance = self.name
        attendance_entry.employee = self.employee
        attendance_entry.attendance_date = self.attendance_date
        attendance_entry.check_in_time = self.check_in_time
        attendance_entry.check_out_time = self.check_out_time
        attendance_entry.working_hours = self.working_hours
        attendance_entry.net_working_hours = self.net_working_hours
        attendance_entry.overtime_hours = self.overtime_hours
        attendance_entry.status = self.status
        attendance_entry.save(ignore_permissions=True)

    def setup_attendance_workflow(self):
        """Setup attendance workflow"""
        # Update attendance workflow status
        workflow_data = {
            "workflow_name": f"Attendance Workflow - {self.attendance_id}",
            "workflow_type": "Attendance",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Approved", "status": "Pending"}
            ]
        }
        
        # Update or create Attendance Workflow DocType
        if frappe.db.exists("Attendance Workflow", self.attendance_id):
            attendance_workflow = frappe.get_doc("Attendance Workflow", self.attendance_id)
            attendance_workflow.update(workflow_data)
            attendance_workflow.save(ignore_permissions=True)
        else:
            attendance_workflow = frappe.new_doc("Attendance Workflow")
            attendance_workflow.update(workflow_data)
            attendance_workflow.name = self.attendance_id
            attendance_workflow.insert(ignore_permissions=True)

    def update_attendance_settings(self):
        """Update attendance settings"""
        # Set attendance permissions
        self.set_attendance_permissions()
        
        # Update attendance workflow
        self.update_attendance_workflow()

    def set_attendance_permissions(self):
        """Set attendance permissions"""
        # Create attendance-specific roles
        attendance_roles = [
            f"Attendance - {self.attendance_id}",
            f"Employee - {self.employee}",
            f"Date - {self.attendance_date}"
        ]
        
        # Ensure roles exist
        for role_name in attendance_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_attendance_workflow(self):
        """Update attendance workflow"""
        # Update attendance workflow status
        workflow_data = {
            "workflow_name": f"Attendance Workflow - {self.attendance_id}",
            "workflow_type": "Attendance",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Approval", "status": "Pending"},
                {"step": "Approved", "status": "Pending"}
            ]
        }
        
        # Update or create Attendance Workflow DocType
        if frappe.db.exists("Attendance Workflow", self.attendance_id):
            attendance_workflow = frappe.get_doc("Attendance Workflow", self.attendance_id)
            attendance_workflow.update(workflow_data)
            attendance_workflow.save(ignore_permissions=True)
        else:
            attendance_workflow = frappe.new_doc("Attendance Workflow")
            attendance_workflow.update(workflow_data)
            attendance_workflow.name = self.attendance_id
            attendance_workflow.insert(ignore_permissions=True)

    def generate_attendance_insights(self):
        """Generate attendance insights"""
        insights = {
            "attendance_id": self.attendance_id,
            "employee": self.employee,
            "attendance_date": self.attendance_date,
            "check_in_time": self.check_in_time,
            "check_out_time": self.check_out_time,
            "working_hours": self.working_hours,
            "net_working_hours": self.net_working_hours,
            "overtime_hours": self.overtime_hours,
            "status": self.status,
            "geolocation": {
                "check_in": {
                    "latitude": self.check_in_latitude,
                    "longitude": self.check_in_longitude,
                    "address": self.check_in_address
                },
                "check_out": {
                    "latitude": self.check_out_latitude,
                    "longitude": self.check_out_longitude,
                    "address": self.check_out_address
                }
            },
            "recommendations": self.generate_recommendations()
        }
        
        self.attendance_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate attendance recommendations"""
        recommendations = []
        
        # Working hours recommendations
        if self.net_working_hours < 8:
            recommendations.append("Consider working additional hours to meet daily target")
        
        if self.overtime_hours > 2:
            recommendations.append("Consider overtime management for work-life balance")
        
        # Location recommendations
        if self.check_in_latitude and self.check_in_longitude:
            employee = frappe.get_doc("Employee", self.employee)
            if employee.office_location:
                office_location = frappe.get_doc("Office Location", employee.office_location)
                distance = self.calculate_distance(
                    self.check_in_latitude, self.check_in_longitude,
                    office_location.latitude, office_location.longitude
                )
                
                if distance > 50:  # 50 meters
                    recommendations.append("Consider checking in from office location")
        
        return recommendations

    def update_attendance_analytics(self):
        """Update attendance analytics"""
        # Update attendance analytics data
        analytics_data = {
            "analytics_name": f"Attendance Analytics - {self.attendance_id}",
            "analytics_type": "Attendance Analytics",
            "metrics": {
                "attendance_id": self.attendance_id,
                "employee": self.employee,
                "attendance_date": self.attendance_date,
                "working_hours": self.working_hours,
                "net_working_hours": self.net_working_hours,
                "overtime_hours": self.overtime_hours,
                "status": self.status
            },
            "insights": self.generate_attendance_insights(),
            "last_updated": now()
        }
        
        # Update or create Attendance Analytics DocType
        if frappe.db.exists("Attendance Analytics", self.attendance_id):
            attendance_analytics = frappe.get_doc("Attendance Analytics", self.attendance_id)
            attendance_analytics.update(analytics_data)
            attendance_analytics.save(ignore_permissions=True)
        else:
            attendance_analytics = frappe.new_doc("Attendance Analytics")
            attendance_analytics.update(analytics_data)
            attendance_analytics.name = self.attendance_id
            attendance_analytics.insert(ignore_permissions=True)

    def sync_attendance_data(self):
        """Sync attendance data across systems"""
        # Sync with external HR systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_attendance_changes(self):
        """Process attendance changes"""
        # Log changes
        self.log_attendance_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_attendance_changes(self):
        """Log attendance changes"""
        frappe.get_doc({
            "doctype": "Attendance Change Log",
            "attendance": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Attendance {self.attendance_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update employee attendance records
        self.update_employee_attendance_records()

    def update_employee_attendance_records(self):
        """Update employee attendance records"""
        # Update employee attendance summary
        frappe.db.sql("""
            UPDATE `tabEmployee`
            SET last_attendance_date = %s,
                total_working_hours = total_working_hours + %s,
                total_overtime_hours = total_overtime_hours + %s
            WHERE name = %s
        """, (self.attendance_date, self.net_working_hours, self.overtime_hours, self.employee))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify HR team
        self.notify_hr_team()
        
        # Notify manager
        self.notify_manager()

    def notify_hr_team(self):
        """Notify HR team"""
        frappe.get_doc({
            "doctype": "Attendance Notification",
            "attendance": self.name,
            "notification_type": "Attendance Update",
            "message": f"Attendance {self.attendance_id} has been updated",
            "recipients": "HR Team",
            "created_date": now()
        }).insert(ignore_permissions=True)

    def notify_manager(self):
        """Notify manager"""
        employee = frappe.get_doc("Employee", self.employee)
        if employee.reports_to:
            frappe.get_doc({
                "doctype": "Attendance Notification",
                "attendance": self.name,
                "notification_type": "Attendance Update",
                "message": f"Attendance {self.attendance_id} has been updated",
                "recipients": employee.reports_to,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync attendance data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_attendance_dashboard_data(self):
        """Get attendance dashboard data"""
        return {
            "attendance_id": self.attendance_id,
            "employee": self.employee,
            "attendance_date": self.attendance_date,
            "check_in_time": self.check_in_time,
            "check_out_time": self.check_out_time,
            "working_hours": self.working_hours,
            "net_working_hours": self.net_working_hours,
            "overtime_hours": self.overtime_hours,
            "status": self.status,
            "geolocation": {
                "check_in": {
                    "latitude": self.check_in_latitude,
                    "longitude": self.check_in_longitude,
                    "address": self.check_in_address
                },
                "check_out": {
                    "latitude": self.check_out_latitude,
                    "longitude": self.check_out_longitude,
                    "address": self.check_out_address
                }
            },
            "insights": self.generate_attendance_insights()
        }

    @frappe.whitelist()
    def check_in(self, latitude=None, longitude=None, address=None):
        """Employee check-in"""
        if self.check_in_time:
            frappe.throw(_("Employee has already checked in"))
        
        self.check_in_time = now()
        self.check_in_latitude = latitude
        self.check_in_longitude = longitude
        self.check_in_address = address
        self.status = "Present"
        self.save()
        
        frappe.msgprint(_("Employee {0} checked in at {1}").format(self.employee, self.check_in_time))
        return self.as_dict()

    @frappe.whitelist()
    def check_out(self, latitude=None, longitude=None, address=None):
        """Employee check-out"""
        if not self.check_in_time:
            frappe.throw(_("Employee must check in before checking out"))
        
        if self.check_out_time:
            frappe.throw(_("Employee has already checked out"))
        
        self.check_out_time = now()
        self.check_out_latitude = latitude
        self.check_out_longitude = longitude
        self.check_out_address = address
        
        # Calculate working hours
        self.calculate_working_hours()
        self.save()
        
        frappe.msgprint(_("Employee {0} checked out at {1}").format(self.employee, self.check_out_time))
        return self.as_dict()

    @frappe.whitelist()
    def start_break(self, break_start_time=None):
        """Start break"""
        if not self.check_in_time:
            frappe.throw(_("Employee must check in before starting break"))
        
        if self.check_out_time:
            frappe.throw(_("Employee cannot start break after check-out"))
        
        self.break_start_time = break_start_time or now()
        self.save()
        
        frappe.msgprint(_("Break started at {0}").format(self.break_start_time))
        return self.as_dict()

    @frappe.whitelist()
    def end_break(self, break_end_time=None):
        """End break"""
        if not self.break_start_time:
            frappe.throw(_("Employee must start break before ending break"))
        
        self.break_end_time = break_end_time or now()
        
        # Calculate working hours
        self.calculate_working_hours()
        self.save()
        
        frappe.msgprint(_("Break ended at {0}").format(self.break_end_time))
        return self.as_dict()

    @frappe.whitelist()
    def approve_attendance(self):
        """Approve attendance"""
        if self.status != "Pending":
            frappe.throw(_("Only pending attendance can be approved"))
        
        self.status = "Approved"
        self.approved_by = frappe.session.user
        self.approved_date = now()
        self.save()
        
        frappe.msgprint(_("Attendance {0} approved").format(self.attendance_id))
        return self.as_dict()

    @frappe.whitelist()
    def reject_attendance(self, reason=None):
        """Reject attendance"""
        if self.status != "Pending":
            frappe.throw(_("Only pending attendance can be rejected"))
        
        self.status = "Rejected"
        self.rejected_by = frappe.session.user
        self.rejected_date = now()
        self.rejection_reason = reason
        self.save()
        
        frappe.msgprint(_("Attendance {0} rejected").format(self.attendance_id))
        return self.as_dict()
