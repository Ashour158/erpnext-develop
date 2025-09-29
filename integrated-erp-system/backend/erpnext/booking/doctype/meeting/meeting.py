# Meeting DocType - Complete Meeting Scheduling System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt, time_diff_in_hours
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class Meeting(Document):
    def autoname(self):
        """Generate unique meeting ID"""
        if not self.meeting_id:
            self.meeting_id = make_autoname("MTG-.YYYY.-.MM.-.#####")
        self.name = self.meeting_id

    def validate(self):
        """Validate meeting data"""
        self.validate_meeting_data()
        self.set_defaults()
        self.validate_meeting_time()
        self.validate_attendees()
        self.check_conflicts()

    def before_save(self):
        """Process before saving"""
        self.update_meeting_settings()
        self.generate_meeting_insights()
        self.calculate_meeting_duration()

    def after_insert(self):
        """Process after inserting new meeting"""
        self.create_meeting_entries()
        self.setup_meeting_workflow()
        self.send_meeting_invitations()

    def on_update(self):
        """Process on meeting update"""
        self.update_meeting_analytics()
        self.sync_meeting_data()
        self.process_meeting_changes()

    def validate_meeting_data(self):
        """Validate meeting information"""
        if not self.meeting_title:
            frappe.throw(_("Meeting title is required"))
        
        if not self.meeting_date:
            frappe.throw(_("Meeting date is required"))
        
        if not self.start_time:
            frappe.throw(_("Start time is required"))
        
        if not self.end_time:
            frappe.throw(_("End time is required"))

    def set_defaults(self):
        """Set default values for new meeting"""
        if not self.meeting_date:
            self.meeting_date = now().date()
        
        if not self.status:
            self.status = "Scheduled"
        
        if not self.meeting_type:
            self.meeting_type = "Internal"
        
        if not self.organizer:
            self.organizer = frappe.session.user

    def validate_meeting_time(self):
        """Validate meeting time"""
        if self.start_time >= self.end_time:
            frappe.throw(_("Start time cannot be greater than or equal to end time"))
        
        # Check if meeting is in the past
        meeting_datetime = datetime.combine(self.meeting_date, self.start_time)
        if meeting_datetime < now():
            frappe.throw(_("Cannot schedule meeting in the past"))

    def validate_attendees(self):
        """Validate meeting attendees"""
        if not self.attendees:
            frappe.throw(_("At least one attendee is required"))
        
        for attendee in self.attendees:
            if not attendee.attendee:
                frappe.throw(_("Attendee is required for all attendees"))
            
            if not frappe.db.exists("User", attendee.attendee):
                frappe.throw(_("Attendee {0} does not exist").format(attendee.attendee))

    def check_conflicts(self):
        """Check for meeting conflicts"""
        for attendee in self.attendees:
            # Check for overlapping meetings
            overlapping_meetings = frappe.get_list("Meeting",
                filters={
                    "status": ["in", ["Scheduled", "In Progress"]],
                    "meeting_date": self.meeting_date,
                    "start_time": ["<", self.end_time],
                    "end_time": [">", self.start_time]
                },
                fields=["name", "meeting_title", "start_time", "end_time"]
            )
            
            # Check if attendee is already in another meeting
            for meeting in overlapping_meetings:
                if meeting.name != self.name:
                    meeting_attendees = frappe.get_list("Meeting Attendee",
                        filters={"meeting": meeting.name, "attendee": attendee.attendee},
                        fields=["name"]
                    )
                    
                    if meeting_attendees:
                        frappe.throw(_("Attendee {0} has a conflicting meeting: {1}").format(
                            attendee.attendee, meeting.meeting_title
                        ))

    def calculate_meeting_duration(self):
        """Calculate meeting duration"""
        if self.start_time and self.end_time:
            self.duration_hours = time_diff_in_hours(self.end_time, self.start_time)
            self.duration_minutes = self.duration_hours * 60

    def create_meeting_entries(self):
        """Create meeting entries"""
        # Create meeting entry
        meeting_entry = frappe.new_doc("Meeting Entry")
        meeting_entry.meeting = self.name
        meeting_entry.meeting_title = self.meeting_title
        meeting_entry.meeting_date = self.meeting_date
        meeting_entry.start_time = self.start_time
        meeting_entry.end_time = self.end_time
        meeting_entry.duration_hours = self.duration_hours
        meeting_entry.meeting_type = self.meeting_type
        meeting_entry.status = self.status
        meeting_entry.save(ignore_permissions=True)

    def setup_meeting_workflow(self):
        """Setup meeting workflow"""
        # Update meeting workflow status
        workflow_data = {
            "workflow_name": f"Meeting Workflow - {self.meeting_id}",
            "workflow_type": "Meeting",
            "steps": [
                {"step": "Scheduled", "status": "Completed"},
                {"step": "In Progress", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create Meeting Workflow DocType
        if frappe.db.exists("Meeting Workflow", self.meeting_id):
            meeting_workflow = frappe.get_doc("Meeting Workflow", self.meeting_id)
            meeting_workflow.update(workflow_data)
            meeting_workflow.save(ignore_permissions=True)
        else:
            meeting_workflow = frappe.new_doc("Meeting Workflow")
            meeting_workflow.update(workflow_data)
            meeting_workflow.name = self.meeting_id
            meeting_workflow.insert(ignore_permissions=True)

    def update_meeting_settings(self):
        """Update meeting settings"""
        # Set meeting permissions
        self.set_meeting_permissions()
        
        # Update meeting workflow
        self.update_meeting_workflow()

    def set_meeting_permissions(self):
        """Set meeting permissions"""
        # Create meeting-specific roles
        meeting_roles = [
            f"Meeting - {self.meeting_id}",
            f"Organizer - {self.organizer}",
            f"Type - {self.meeting_type}"
        ]
        
        # Ensure roles exist
        for role_name in meeting_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_meeting_workflow(self):
        """Update meeting workflow"""
        # Update meeting workflow status
        workflow_data = {
            "workflow_name": f"Meeting Workflow - {self.meeting_id}",
            "workflow_type": "Meeting",
            "steps": [
                {"step": "Scheduled", "status": "Completed"},
                {"step": "In Progress", "status": "Pending"},
                {"step": "Completed", "status": "Pending"}
            ]
        }
        
        # Update or create Meeting Workflow DocType
        if frappe.db.exists("Meeting Workflow", self.meeting_id):
            meeting_workflow = frappe.get_doc("Meeting Workflow", self.meeting_id)
            meeting_workflow.update(workflow_data)
            meeting_workflow.save(ignore_permissions=True)
        else:
            meeting_workflow = frappe.new_doc("Meeting Workflow")
            meeting_workflow.update(workflow_data)
            meeting_workflow.name = self.meeting_id
            meeting_workflow.insert(ignore_permissions=True)

    def generate_meeting_insights(self):
        """Generate meeting insights"""
        insights = {
            "meeting_id": self.meeting_id,
            "meeting_title": self.meeting_title,
            "meeting_date": self.meeting_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_hours": self.duration_hours,
            "meeting_type": self.meeting_type,
            "status": self.status,
            "organizer": self.organizer,
            "attendees_count": len(self.attendees),
            "location": self.location,
            "meeting_room": self.meeting_room,
            "recommendations": self.generate_recommendations()
        }
        
        self.meeting_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate meeting recommendations"""
        recommendations = []
        
        # Duration recommendations
        if self.duration_hours > 2:
            recommendations.append("Consider scheduling breaks for long meetings")
        
        # Attendee recommendations
        if len(self.attendees) > 10:
            recommendations.append("Consider using a larger meeting room for many attendees")
        
        # Time recommendations
        if self.start_time.hour < 9 or self.start_time.hour > 17:
            recommendations.append("Consider scheduling during business hours")
        
        return recommendations

    def update_meeting_analytics(self):
        """Update meeting analytics"""
        # Update meeting analytics data
        analytics_data = {
            "analytics_name": f"Meeting Analytics - {self.meeting_id}",
            "analytics_type": "Meeting Analytics",
            "metrics": {
                "meeting_id": self.meeting_id,
                "meeting_title": self.meeting_title,
                "meeting_date": self.meeting_date,
                "duration_hours": self.duration_hours,
                "meeting_type": self.meeting_type,
                "status": self.status,
                "attendees_count": len(self.attendees)
            },
            "insights": self.generate_meeting_insights(),
            "last_updated": now()
        }
        
        # Update or create Meeting Analytics DocType
        if frappe.db.exists("Meeting Analytics", self.meeting_id):
            meeting_analytics = frappe.get_doc("Meeting Analytics", self.meeting_id)
            meeting_analytics.update(analytics_data)
            meeting_analytics.save(ignore_permissions=True)
        else:
            meeting_analytics = frappe.new_doc("Meeting Analytics")
            meeting_analytics.update(analytics_data)
            meeting_analytics.name = self.meeting_id
            meeting_analytics.insert(ignore_permissions=True)

    def sync_meeting_data(self):
        """Sync meeting data across systems"""
        # Sync with external calendar systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_meeting_changes(self):
        """Process meeting changes"""
        # Log changes
        self.log_meeting_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_meeting_changes(self):
        """Log meeting changes"""
        frappe.get_doc({
            "doctype": "Meeting Change Log",
            "meeting": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Meeting {self.meeting_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update attendee calendar records
        self.update_attendee_calendar_records()

    def update_attendee_calendar_records(self):
        """Update attendee calendar records"""
        for attendee in self.attendees:
            # Update attendee calendar
            frappe.db.sql("""
                UPDATE `tabUser`
                SET last_meeting_date = %s,
                    total_meetings = (
                        SELECT COUNT(*) FROM `tabMeeting Attendee`
                        WHERE attendee = %s AND status = 'Scheduled'
                    )
                WHERE name = %s
            """, (self.meeting_date, attendee.attendee, attendee.attendee))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify attendees
        self.notify_attendees()
        
        # Notify organizer
        self.notify_organizer()

    def notify_attendees(self):
        """Notify attendees"""
        for attendee in self.attendees:
            frappe.get_doc({
                "doctype": "Meeting Notification",
                "meeting": self.name,
                "notification_type": "Meeting Update",
                "message": f"Meeting {self.meeting_id} has been updated",
                "recipients": attendee.attendee,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def notify_organizer(self):
        """Notify organizer"""
        frappe.get_doc({
            "doctype": "Meeting Notification",
            "meeting": self.name,
            "notification_type": "Meeting Update",
            "message": f"Meeting {self.meeting_id} has been updated",
            "recipients": self.organizer,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def send_meeting_invitations(self):
        """Send meeting invitations"""
        for attendee in self.attendees:
            # Send email invitation
            subject = f"Meeting Invitation: {self.meeting_title}"
            message = f"""
            You have been invited to a meeting:
            
            Title: {self.meeting_title}
            Date: {self.meeting_date}
            Time: {self.start_time} - {self.end_time}
            Location: {self.location or 'TBD'}
            Organizer: {self.organizer}
            
            Please confirm your attendance.
            """
            
            frappe.sendmail(
                recipients=attendee.attendee,
                subject=subject,
                content=message
            )

    def sync_with_external_system(self):
        """Sync meeting data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_meeting_dashboard_data(self):
        """Get meeting dashboard data"""
        return {
            "meeting_id": self.meeting_id,
            "meeting_title": self.meeting_title,
            "meeting_date": self.meeting_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_hours": self.duration_hours,
            "meeting_type": self.meeting_type,
            "status": self.status,
            "organizer": self.organizer,
            "attendees_count": len(self.attendees),
            "location": self.location,
            "meeting_room": self.meeting_room,
            "insights": self.generate_meeting_insights()
        }

    @frappe.whitelist()
    def start_meeting(self):
        """Start meeting"""
        if self.status != "Scheduled":
            frappe.throw(_("Only scheduled meetings can be started"))
        
        self.status = "In Progress"
        self.actual_start_time = now()
        self.save()
        
        frappe.msgprint(_("Meeting {0} started").format(self.meeting_id))
        return self.as_dict()

    @frappe.whitelist()
    def end_meeting(self):
        """End meeting"""
        if self.status != "In Progress":
            frappe.throw(_("Only meetings in progress can be ended"))
        
        self.status = "Completed"
        self.actual_end_time = now()
        self.save()
        
        frappe.msgprint(_("Meeting {0} completed").format(self.meeting_id))
        return self.as_dict()

    @frappe.whitelist()
    def cancel_meeting(self, reason=None):
        """Cancel meeting"""
        if self.status == "Completed":
            frappe.throw(_("Completed meetings cannot be cancelled"))
        
        self.status = "Cancelled"
        self.cancelled_date = now()
        self.cancelled_by = frappe.session.user
        self.cancellation_reason = reason
        self.save()
        
        frappe.msgprint(_("Meeting {0} cancelled").format(self.meeting_id))
        return self.as_dict()

    @frappe.whitelist()
    def reschedule_meeting(self, new_date, new_start_time, new_end_time):
        """Reschedule meeting"""
        if self.status == "Completed":
            frappe.throw(_("Completed meetings cannot be rescheduled"))
        
        self.meeting_date = new_date
        self.start_time = new_start_time
        self.end_time = new_end_time
        self.calculate_meeting_duration()
        self.save()
        
        frappe.msgprint(_("Meeting {0} rescheduled to {1} at {2}").format(
            self.meeting_id, new_date, new_start_time
        ))
        return self.as_dict()

    @frappe.whitelist()
    def add_attendee(self, attendee, role="Attendee"):
        """Add attendee to meeting"""
        # Check if attendee already exists
        existing_attendee = frappe.get_list("Meeting Attendee",
            filters={"meeting": self.name, "attendee": attendee},
            fields=["name"]
        )
        
        if existing_attendee:
            frappe.throw(_("Attendee {0} is already in the meeting").format(attendee))
        
        # Add attendee
        self.append("attendees", {
            "attendee": attendee,
            "role": role,
            "status": "Invited"
        })
        self.save()
        
        frappe.msgprint(_("Attendee {0} added to meeting").format(attendee))
        return self.as_dict()

    @frappe.whitelist()
    def remove_attendee(self, attendee):
        """Remove attendee from meeting"""
        # Find attendee
        for attendee_doc in self.attendees:
            if attendee_doc.attendee == attendee:
                self.remove(attendee_doc)
                break
        
        self.save()
        
        frappe.msgprint(_("Attendee {0} removed from meeting").format(attendee))
        return self.as_dict()

    @frappe.whitelist()
    def duplicate_meeting(self):
        """Duplicate meeting"""
        new_meeting = frappe.copy_doc(self)
        new_meeting.meeting_id = None
        new_meeting.status = "Scheduled"
        new_meeting.meeting_date = add_days(self.meeting_date, 1)
        new_meeting.save(ignore_permissions=True)
        
        frappe.msgprint(_("Meeting duplicated as {0}").format(new_meeting.meeting_id))
        return new_meeting.as_dict()
