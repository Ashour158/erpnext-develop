# Moment Reaction DocType - Complete Reaction System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta

class MomentReaction(Document):
    def autoname(self):
        """Generate unique reaction ID"""
        if not self.reaction_id:
            self.reaction_id = make_autoname("REA-.YYYY.-.MM.-.#####")
        self.name = self.reaction_id

    def validate(self):
        """Validate reaction data"""
        self.validate_reaction_data()
        self.set_defaults()
        self.validate_user_data()
        self.validate_moment_data()

    def before_save(self):
        """Process before saving"""
        self.update_reaction_settings()
        self.generate_reaction_insights()

    def after_insert(self):
        """Process after inserting new reaction"""
        self.create_reaction_entries()
        self.update_moment_reaction_count()

    def on_update(self):
        """Process on reaction update"""
        self.update_reaction_analytics()
        self.sync_reaction_data()
        self.process_reaction_changes()

    def validate_reaction_data(self):
        """Validate reaction information"""
        if not self.moment:
            frappe.throw(_("Moment is required"))
        
        if not self.user:
            frappe.throw(_("User is required"))
        
        if not self.reaction_type:
            frappe.throw(_("Reaction type is required"))

    def set_defaults(self):
        """Set default values for new reaction"""
        if not self.reaction_date:
            self.reaction_date = now()
        
        if not self.status:
            self.status = "Active"

    def validate_user_data(self):
        """Validate user information"""
        if not frappe.db.exists("User", self.user):
            frappe.throw(_("User {0} does not exist").format(self.user))

    def validate_moment_data(self):
        """Validate moment information"""
        if not frappe.db.exists("Moment", self.moment):
            frappe.throw(_("Moment {0} does not exist").format(self.moment))

    def create_reaction_entries(self):
        """Create reaction entries"""
        # Create reaction entry
        reaction_entry = frappe.new_doc("Reaction Entry")
        reaction_entry.reaction = self.name
        reaction_entry.moment = self.moment
        reaction_entry.user = self.user
        reaction_entry.reaction_type = self.reaction_type
        reaction_entry.reaction_date = self.reaction_date
        reaction_entry.status = self.status
        reaction_entry.save(ignore_permissions=True)

    def update_moment_reaction_count(self):
        """Update moment reaction count"""
        # Get moment document
        moment = frappe.get_doc("Moment", self.moment)
        
        # Update reaction count based on type
        if self.reaction_type == "Like":
            moment.likes_count = (moment.likes_count or 0) + 1
        elif self.reaction_type == "Love":
            moment.love_count = (moment.love_count or 0) + 1
        elif self.reaction_type == "Care":
            moment.care_count = (moment.care_count or 0) + 1
        elif self.reaction_type == "Angry":
            moment.angry_count = (moment.angry_count or 0) + 1
        
        moment.save(ignore_permissions=True)

    def update_reaction_settings(self):
        """Update reaction settings"""
        # Set reaction permissions
        self.set_reaction_permissions()
        
        # Update reaction workflow
        self.update_reaction_workflow()

    def set_reaction_permissions(self):
        """Set reaction permissions"""
        # Create reaction-specific roles
        reaction_roles = [
            f"Reaction - {self.reaction_id}",
            f"User - {self.user}",
            f"Type - {self.reaction_type}"
        ]
        
        # Ensure roles exist
        for role_name in reaction_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_reaction_workflow(self):
        """Update reaction workflow"""
        # Update reaction workflow status
        workflow_data = {
            "workflow_name": f"Reaction Workflow - {self.reaction_id}",
            "workflow_type": "Reaction",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Active", "status": "Pending"}
            ]
        }
        
        # Update or create Reaction Workflow DocType
        if frappe.db.exists("Reaction Workflow", self.reaction_id):
            reaction_workflow = frappe.get_doc("Reaction Workflow", self.reaction_id)
            reaction_workflow.update(workflow_data)
            reaction_workflow.save(ignore_permissions=True)
        else:
            reaction_workflow = frappe.new_doc("Reaction Workflow")
            reaction_workflow.update(workflow_data)
            reaction_workflow.name = self.reaction_id
            reaction_workflow.insert(ignore_permissions=True)

    def generate_reaction_insights(self):
        """Generate reaction insights"""
        insights = {
            "reaction_id": self.reaction_id,
            "moment": self.moment,
            "user": self.user,
            "reaction_type": self.reaction_type,
            "reaction_date": self.reaction_date,
            "status": self.status,
            "recommendations": self.generate_recommendations()
        }
        
        self.reaction_insights = json.dumps(insights)

    def generate_recommendations(self):
        """Generate reaction recommendations"""
        recommendations = []
        
        # Reaction type recommendations
        if self.reaction_type == "Angry":
            recommendations.append("Consider providing constructive feedback")
        
        # Engagement recommendations
        recommendations.append("Continue engaging with content to build community")
        
        return recommendations

    def update_reaction_analytics(self):
        """Update reaction analytics"""
        # Update reaction analytics data
        analytics_data = {
            "analytics_name": f"Reaction Analytics - {self.reaction_id}",
            "analytics_type": "Reaction Analytics",
            "metrics": {
                "reaction_id": self.reaction_id,
                "moment": self.moment,
                "user": self.user,
                "reaction_type": self.reaction_type,
                "status": self.status
            },
            "insights": self.generate_reaction_insights(),
            "last_updated": now()
        }
        
        # Update or create Reaction Analytics DocType
        if frappe.db.exists("Reaction Analytics", self.reaction_id):
            reaction_analytics = frappe.get_doc("Reaction Analytics", self.reaction_id)
            reaction_analytics.update(analytics_data)
            reaction_analytics.save(ignore_permissions=True)
        else:
            reaction_analytics = frappe.new_doc("Reaction Analytics")
            reaction_analytics.update(analytics_data)
            reaction_analytics.name = self.reaction_id
            reaction_analytics.insert(ignore_permissions=True)

    def sync_reaction_data(self):
        """Sync reaction data across systems"""
        # Sync with external social media systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_reaction_changes(self):
        """Process reaction changes"""
        # Log changes
        self.log_reaction_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_reaction_changes(self):
        """Log reaction changes"""
        frappe.get_doc({
            "doctype": "Reaction Change Log",
            "reaction": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Reaction {self.reaction_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update user reaction records
        self.update_user_reaction_records()

    def update_user_reaction_records(self):
        """Update user reaction records"""
        # Update user reaction summary
        frappe.db.sql("""
            UPDATE `tabUser`
            SET total_reactions = (
                SELECT COUNT(*) FROM `tabMoment Reaction`
                WHERE user = %s AND status = 'Active'
            )
            WHERE name = %s
        """, (self.user, self.user))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify moment owner
        self.notify_moment_owner()

    def notify_moment_owner(self):
        """Notify moment owner"""
        moment = frappe.get_doc("Moment", self.moment)
        if moment.user != self.user:
            frappe.get_doc({
                "doctype": "Reaction Notification",
                "reaction": self.name,
                "notification_type": "New Reaction",
                "message": f"New {self.reaction_type} reaction on your moment",
                "recipients": moment.user,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync reaction data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_reaction_dashboard_data(self):
        """Get reaction dashboard data"""
        return {
            "reaction_id": self.reaction_id,
            "moment": self.moment,
            "user": self.user,
            "reaction_type": self.reaction_type,
            "reaction_date": self.reaction_date,
            "status": self.status,
            "insights": self.generate_reaction_insights()
        }

    @frappe.whitelist()
    def change_reaction_type(self, new_reaction_type):
        """Change reaction type"""
        old_reaction_type = self.reaction_type
        self.reaction_type = new_reaction_type
        self.save()
        
        # Update moment reaction counts
        self.update_moment_reaction_counts(old_reaction_type, new_reaction_type)
        
        frappe.msgprint(_("Reaction type changed from {0} to {1}").format(old_reaction_type, new_reaction_type))
        return self.as_dict()

    def update_moment_reaction_counts(self, old_type, new_type):
        """Update moment reaction counts"""
        moment = frappe.get_doc("Moment", self.moment)
        
        # Decrease old reaction count
        if old_type == "Like":
            moment.likes_count = max((moment.likes_count or 0) - 1, 0)
        elif old_type == "Love":
            moment.love_count = max((moment.love_count or 0) - 1, 0)
        elif old_type == "Care":
            moment.care_count = max((moment.care_count or 0) - 1, 0)
        elif old_type == "Angry":
            moment.angry_count = max((moment.angry_count or 0) - 1, 0)
        
        # Increase new reaction count
        if new_type == "Like":
            moment.likes_count = (moment.likes_count or 0) + 1
        elif new_type == "Love":
            moment.love_count = (moment.love_count or 0) + 1
        elif new_type == "Care":
            moment.care_count = (moment.care_count or 0) + 1
        elif new_type == "Angry":
            moment.angry_count = (moment.angry_count or 0) + 1
        
        moment.save(ignore_permissions=True)

    @frappe.whitelist()
    def remove_reaction(self):
        """Remove reaction"""
        if self.status == "Removed":
            frappe.throw(_("Reaction is already removed"))
        
        self.status = "Removed"
        self.removed_date = now()
        self.removed_by = frappe.session.user
        self.save()
        
        # Update moment reaction count
        self.update_moment_reaction_count_removal()
        
        frappe.msgprint(_("Reaction {0} removed").format(self.reaction_id))
        return self.as_dict()

    def update_moment_reaction_count_removal(self):
        """Update moment reaction count on removal"""
        moment = frappe.get_doc("Moment", self.moment)
        
        # Decrease reaction count
        if self.reaction_type == "Like":
            moment.likes_count = max((moment.likes_count or 0) - 1, 0)
        elif self.reaction_type == "Love":
            moment.love_count = max((moment.love_count or 0) - 1, 0)
        elif self.reaction_type == "Care":
            moment.care_count = max((moment.care_count or 0) - 1, 0)
        elif self.reaction_type == "Angry":
            moment.angry_count = max((moment.angry_count or 0) - 1, 0)
        
        moment.save(ignore_permissions=True)
