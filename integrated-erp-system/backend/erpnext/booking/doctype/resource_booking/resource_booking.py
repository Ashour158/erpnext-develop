# Resource Booking DocType - Complete Resource Booking System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt, time_diff_in_hours
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class ResourceBooking(Document):
    def autoname(self):
        """Generate unique resource booking ID"""
        if not self.booking_id:
            self.booking_id = make_autoname("RB-.YYYY.-.MM.-.#####")
        self.name = self.booking_id

    def validate(self):
        """Validate resource booking data"""
        self.validate_booking_data()
        self.set_defaults()
        self.validate_resource_data()
        self.validate_booking_time()
        self.check_resource_availability()

    def before_save(self):
        """Process before saving"""
        self.update_booking_settings()
        self.generate_booking_insights()
        self.calculate_booking_duration()

    def after_insert(self):
        """Process after inserting new booking"""
        self.create_booking_entries()
        self.setup_booking_workflow()
        self.send_booking_confirmation()

    def on_update(self):
        """Process on booking update"""
        self.update_booking_analytics()
        self.sync_booking_data()
        self.process_booking_changes()

    def validate_booking_data(self):
        """Validate booking information"""
        if not self.resource:
            frappe.throw(_("Resource is required"))
        
        if not self.booking_date:
            frappe.throw(_("Booking date is required"))
        
        if not self.start_time:
            frappe.throw(_("Start time is required"))
        
        if not self.end_time:
            frappe.throw(_("End time is required"))
        
        if not self.booked_by:
            frappe.throw(_("Booked by is required"))

    def set_defaults(self):
        """Set default values for new booking"""
        if not self.booking_date:
            self.booking_date = now().date()
        
        if not self.status:
            self.status = "Booked"
        
        if not self.booking_type:
            self.booking_type = "Internal"
        
        if not self.booked_by:
            self.booked_by = frappe.session.user

    def validate_resource_data(self):
        """Validate resource information"""
        if not frappe.db.exists("Resource", self.resource):
            frappe.throw(_("Resource {0} does not exist").format(self.resource))

    def validate_booking_time(self):
        """Validate booking time"""
        if self.start_time >= self.end_time:
            frappe.throw(_("Start time cannot be greater than or equal to end time"))
        
        # Check if booking is in the past
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        if booking_datetime < now():
            frappe.throw(_("Cannot book resource in the past"))

    def check_resource_availability(self):
        """Check resource availability"""
        # Check for overlapping bookings
        overlapping_bookings = frappe.get_list("Resource Booking",
            filters={
                "resource": self.resource,
                "status": ["in", ["Booked", "In Use"]],
                "booking_date": self.booking_date,
                "start_time": ["<", self.end_time],
                "end_time": [">", self.start_time]
            },
            fields=["name", "booked_by", "start_time", "end_time"]
        )
        
        # Exclude current booking from conflict check
        overlapping_bookings = [b for b in overlapping_bookings if b.name != self.name]
        
        if overlapping_bookings:
            frappe.throw(_("Resource {0} is already booked during this time").format(self.resource))

    def calculate_booking_duration(self):
        """Calculate booking duration"""
        if self.start_time and self.end_time:
            self.duration_hours = time_diff_in_hours(self.end_time, self.start_time)
            self.duration_minutes = self.duration_hours * 60

    def create_booking_entries(self):
        """Create booking entries"""
        # Create booking entry
        booking_entry = frappe.new_doc("Resource Booking Entry")
        booking_entry.booking = self.name
        booking_entry.resource = self.resource
        booking_entry.booking_date = self.booking_date
        booking_entry.start_time = self.start_time
        booking_entry.end_time = self.end_time
        booking_entry.duration_hours = self.duration_hours
        booking_entry.booking_type = self.booking_type
        booking_entry.status = self.status
        booking_entry.save(ignore_permissions=True)

    def setup_booking_workflow(self):
        """Setup booking workflow"""
        # Update booking workflow status
        workflow_data = {
            "workflow_name": f"Resource Booking Workflow - {self.booking_id}",
            "workflow_type": "Resource Booking",
            "steps": [
                {"step": "Booked", "status": "Completed"},
                {"step": "In Use", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create Resource Booking Workflow DocType
        if frappe.db.exists("Resource Booking Workflow", self.booking_id):
            booking_workflow = frappe.get_doc("Resource Booking Workflow", self.booking_id)
            booking_workflow.update(workflow_data)
            booking_workflow.save(ignore_permissions=True)
        else:
            booking_workflow = frappe.new_doc("Resource Booking Workflow")
            booking_workflow.update(workflow_data)
            booking_workflow.name = self.booking_id
            booking_workflow.insert(ignore_permissions=True)

    def update_booking_settings(self):
        """Update booking settings"""
        # Set booking permissions
        self.set_booking_permissions()
        
        # Update booking workflow
        self.update_booking_workflow()

    def set_booking_permissions(self):
        """Set booking permissions"""
        # Create booking-specific roles
        booking_roles = [
            f"Resource Booking - {self.booking_id}",
            f"Resource - {self.resource}",
            f"Booked By - {self.booked_by}"
        ]
        
        # Ensure roles exist
        for role_name in booking_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_booking_workflow(self):
        """Update booking workflow"""
        # Update booking workflow status
        workflow_data = {
            "workflow_name": f"Resource Booking Workflow - {self.booking_id}",
            "workflow_type": "Resource Booking",
            "steps": [
                {"step": "Booked", "status": "Completed"},
                {"step": "In Use", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create Resource Booking Workflow DocType
        if frappe.db.exists("Resource Booking Workflow", self.booking_id):
            booking_workflow = frappe.get_doc("Resource Booking Workflow", self.booking_id)
            booking_workflow.update(workflow_data)
            booking_workflow.save(ignore_permissions=True)
        else:
            booking_workflow = frappe.new_doc("Resource Booking Workflow")
            booking_workflow.update(workflow_data)
            booking_workflow.name = self.booking_id
            booking_workflow.insert(ignore_permissions=True)

    def generate_booking_insights(self):
        """Generate booking insights"""
        insights = {
            "booking_id": self.booking_id,
            "resource": self.resource,
            "booking_date": self.booking_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_hours": self.duration_hours,
            "booking_type": self.booking_type,
            "status": self.status,
            "booked_by": self.booked_by,
            "purpose": self.purpose,
            "location": self.location,
            "recommendations": self.generate_recommendations()
        }
        
        self.booking_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate booking recommendations"""
        recommendations = []
        
        # Duration recommendations
        if self.duration_hours > 4:
            recommendations.append("Consider scheduling breaks for long bookings")
        
        # Time recommendations
        if self.start_time.hour < 9 or self.start_time.hour > 17:
            recommendations.append("Consider booking during business hours")
        
        # Resource recommendations
        resource = frappe.get_doc("Resource", self.resource)
        if resource.capacity and self.attendees_count > resource.capacity:
            recommendations.append("Consider booking a larger resource")
        
        return recommendations

    def update_booking_analytics(self):
        """Update booking analytics"""
        # Update booking analytics data
        analytics_data = {
            "analytics_name": f"Resource Booking Analytics - {self.booking_id}",
            "analytics_type": "Resource Booking Analytics",
            "metrics": {
                "booking_id": self.booking_id,
                "resource": self.resource,
                "booking_date": self.booking_date,
                "duration_hours": self.duration_hours,
                "booking_type": self.booking_type,
                "status": self.status,
                "booked_by": self.booked_by
            },
            "insights": self.generate_booking_insights(),
            "last_updated": now()
        }
        
        # Update or create Resource Booking Analytics DocType
        if frappe.db.exists("Resource Booking Analytics", self.booking_id):
            booking_analytics = frappe.get_doc("Resource Booking Analytics", self.booking_id)
            booking_analytics.update(analytics_data)
            booking_analytics.save(ignore_permissions=True)
        else:
            booking_analytics = frappe.new_doc("Resource Booking Analytics")
            booking_analytics.update(analytics_data)
            booking_analytics.name = self.booking_id
            booking_analytics.insert(ignore_permissions=True)

    def sync_booking_data(self):
        """Sync booking data across systems"""
        # Sync with external booking systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_booking_changes(self):
        """Process booking changes"""
        # Log changes
        self.log_booking_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_booking_changes(self):
        """Log booking changes"""
        frappe.get_doc({
            "doctype": "Resource Booking Change Log",
            "booking": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Resource Booking {self.booking_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update resource booking records
        self.update_resource_booking_records()

    def update_resource_booking_records(self):
        """Update resource booking records"""
        # Update resource booking summary
        frappe.db.sql("""
            UPDATE `tabResource`
            SET last_booking_date = %s,
                total_bookings = (
                    SELECT COUNT(*) FROM `tabResource Booking`
                    WHERE resource = %s AND status = 'Booked'
                )
            WHERE name = %s
        """, (self.booking_date, self.resource, self.resource))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify resource manager
        self.notify_resource_manager()
        
        # Notify booked by user
        self.notify_booked_by_user()

    def notify_resource_manager(self):
        """Notify resource manager"""
        resource = frappe.get_doc("Resource", self.resource)
        if resource.manager:
            frappe.get_doc({
                "doctype": "Resource Booking Notification",
                "booking": self.name,
                "notification_type": "Resource Booking Update",
                "message": f"Resource Booking {self.booking_id} has been updated",
                "recipients": resource.manager,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def notify_booked_by_user(self):
        """Notify booked by user"""
        frappe.get_doc({
            "doctype": "Resource Booking Notification",
            "booking": self.name,
            "notification_type": "Resource Booking Update",
            "message": f"Resource Booking {self.booking_id} has been updated",
            "recipients": self.booked_by,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def send_booking_confirmation(self):
        """Send booking confirmation"""
        # Send email confirmation
        subject = f"Resource Booking Confirmation: {self.resource}"
        message = f"""
        Your resource booking has been confirmed:
        
        Resource: {self.resource}
        Date: {self.booking_date}
        Time: {self.start_time} - {self.end_time}
        Duration: {self.duration_hours} hours
        Purpose: {self.purpose or 'N/A'}
        Location: {self.location or 'N/A'}
        
        Please arrive on time and follow resource usage guidelines.
        """
        
        frappe.sendmail(
            recipients=self.booked_by,
            subject=subject,
            content=message
        )

    def sync_with_external_system(self):
        """Sync booking data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_booking_dashboard_data(self):
        """Get booking dashboard data"""
        return {
            "booking_id": self.booking_id,
            "resource": self.resource,
            "booking_date": self.booking_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_hours": self.duration_hours,
            "booking_type": self.booking_type,
            "status": self.status,
            "booked_by": self.booked_by,
            "purpose": self.purpose,
            "location": self.location,
            "insights": self.generate_booking_insights()
        }

    @frappe.whitelist()
    def start_booking(self):
        """Start resource usage"""
        if self.status != "Booked":
            frappe.throw(_("Only booked resources can be started"))
        
        self.status = "In Use"
        self.actual_start_time = now()
        self.save()
        
        frappe.msgprint(_("Resource {0} usage started").format(self.resource))
        return self.as_dict()

    @frappe.whitelist()
    def end_booking(self):
        """End resource usage"""
        if self.status != "In Use":
            frappe.throw(_("Only resources in use can be ended"))
        
        self.status = "Completed"
        self.actual_end_time = now()
        self.save()
        
        frappe.msgprint(_("Resource {0} usage completed").format(self.resource))
        return self.as_dict()

    @frappe.whitelist()
    def cancel_booking(self, reason=None):
        """Cancel booking"""
        if self.status == "Completed":
            frappe.throw(_("Completed bookings cannot be cancelled"))
        
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.cancelled_by = frappe.session.user
        self.cancellation_reason = reason
        self.save()
        
        frappe.msgprint(_("Resource Booking {0} cancelled").format(self.booking_id))
        return self.as_dict()

    @frappe.whitelist()
    def reschedule_booking(self, new_date, new_start_time, new_end_time):
        """Reschedule booking"""
        if self.status == "Completed":
            frappe.throw(_("Completed bookings cannot be rescheduled"))
        
        self.booking_date = new_date
        self.start_time = new_start_time
        self.end_time = new_end_time
        self.calculate_booking_duration()
        self.save()
        
        frappe.msgprint(_("Resource Booking {0} rescheduled to {1} at {2}").format(
            self.booking_id, new_date, new_start_time
        ))
        return self.as_dict()

    @frappe.whitelist()
    def extend_booking(self, new_end_time):
        """Extend booking"""
        if self.status not in ["Booked", "In Use"]:
            frappe.throw(_("Only active bookings can be extended"))
        
        self.end_time = new_end_time
        self.calculate_booking_duration()
        self.save()
        
        frappe.msgprint(_("Resource Booking {0} extended to {1}").format(
            self.booking_id, new_end_time
        ))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_booking(self):
        """Duplicate booking"""
        new_booking = frappe.copy_doc(self)
        new_booking.booking_id = None
        new_booking.status = "Booked"
        new_booking.booking_date = add_days(self.booking_date, 1)
        new_booking.save(ignore_permissions=True)
        
        frappe.msgprint(_("Resource Booking duplicated as {0}").format(new_booking.booking_id))
        return new_booking.as_dict()
