# Moment DocType - Complete Social Feed System

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time, flt
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests

class Moment(Document):
    def autoname(self):
        """Generate unique moment ID"""
        if not self.moment_id:
            self.moment_id = make_autoname("MOM-.YYYY.-.MM.-.#####")
        self.name = self.moment_id

    def validate(self):
        """Validate moment data"""
        self.validate_moment_data()
        self.set_defaults()
        self.validate_user_data()
        self.validate_content()

    def before_save(self):
        """Process before saving"""
        self.update_moment_settings()
        self.generate_moment_insights()

    def after_insert(self):
        """Process after inserting new moment"""
        self.create_moment_entries()
        self.setup_moment_workflow()
        self.notify_mentioned_users()

    def on_update(self):
        """Process on moment update"""
        self.update_moment_analytics()
        self.sync_moment_data()
        self.process_moment_changes()

    def validate_moment_data(self):
        """Validate moment information"""
        if not self.user:
            frappe.throw(_("User is required"))
        
        if not self.content:
            frappe.throw(_("Content is required"))
        
        if not self.moment_type:
            frappe.throw(_("Moment type is required"))

    def set_defaults(self):
        """Set default values for new moment"""
        if not self.moment_date:
            self.moment_date = now()
        
        if not self.status:
            self.status = "Active"
        
        if not self.visibility:
            self.visibility = "Public"

    def validate_user_data(self):
        """Validate user information"""
        if not frappe.db.exists("User", self.user):
            frappe.throw(_("User {0} does not exist").format(self.user))

    def validate_content(self):
        """Validate moment content"""
        # Check content length
        if len(self.content) > 2000:
            frappe.throw(_("Content cannot exceed 2000 characters"))

    def create_moment_entries(self):
        """Create moment entries"""
        # Create moment entry
        moment_entry = frappe.new_doc("Moment Entry")
        moment_entry.moment = self.name
        moment_entry.user = self.user
        moment_entry.content = self.content
        moment_entry.moment_type = self.moment_type
        moment_entry.visibility = self.visibility
        moment_entry.status = self.status
        moment_entry.save(ignore_permissions=True)

    def setup_moment_workflow(self):
        """Setup moment workflow"""
        # Update moment workflow status
        workflow_data = {
            "workflow_name": f"Moment Workflow - {self.moment_id}",
            "workflow_type": "Moment",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Published", "status": "Pending"}
            ]
        }
        
        # Update or create Moment Workflow DocType
        if frappe.db.exists("Moment Workflow", self.moment_id):
            moment_workflow = frappe.get_doc("Moment Workflow", self.moment_id)
            moment_workflow.update(workflow_data)
            moment_workflow.save(ignore_permissions=True)
        else:
            moment_workflow = frappe.new_doc("Moment Workflow")
            moment_workflow.update(workflow_data)
            moment_workflow.name = self.moment_id
            moment_workflow.insert(ignore_permissions=True)

    def update_moment_settings(self):
        """Update moment settings"""
        # Set moment permissions
        self.set_moment_permissions()
        
        # Update moment workflow
        self.update_moment_workflow()

    def set_moment_permissions(self):
        """Set moment permissions"""
        # Create moment-specific roles
        moment_roles = [
            f"Moment - {self.moment_id}",
            f"User - {self.user}",
            f"Type - {self.moment_type}"
        ]
        
        # Ensure roles exist
        for role_name in moment_roles:
            if not frappe.db.exists("Role", role_name):
                role = frappe.new_doc("Role")
                role.role_name = role_name
                role.save(ignore_permissions=True)

    def update_moment_workflow(self):
        """Update moment workflow"""
        # Update moment workflow status
        workflow_data = {
            "workflow_name": f"Moment Workflow - {self.moment_id}",
            "workflow_type": "Moment",
            "steps": [
                {"step": "Draft", "status": "Completed"},
                {"step": "Review", "status": "Pending"},
                {"step": "Published", "status": "Pending"}
            ]
        }
        
        # Update or create Moment Workflow DocType
        if frappe.db.exists("Moment Workflow", self.moment_id):
            moment_workflow = frappe.get_doc("Moment Workflow", self.moment_id)
            moment_workflow.update(workflow_data)
            moment_workflow.save(ignore_permissions=True)
        else:
            moment_workflow = frappe.new_doc("Moment Workflow")
            moment_workflow.update(workflow_data)
            moment_workflow.name = self.moment_id
            moment_workflow.insert(ignore_permissions=True)

    def generate_moment_insights(self):
        """Generate moment insights"""
        insights = {
            "moment_id": self.moment_id,
            "user": self.user,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "moment_type": self.moment_type,
            "visibility": self.visibility,
            "status": self.status,
            "likes_count": self.likes_count or 0,
            "comments_count": self.comments_count or 0,
            "shares_count": self.shares_count or 0,
            "location": self.location,
            "mentioned_users": self.get_mentioned_users(),
            "hashtags": self.get_hashtags(),
            "recommendations": self.generate_recommendations()
        }
        
        self.moment_insights = json.dumps(insights)

    def get_mentioned_users(self):
        """Get mentioned users from content"""
        mentioned_users = []
        content = self.content
        
        # Find @mentions in content
        import re
        mentions = re.findall(r'@(\w+)', content)
        
        for mention in mentions:
            if frappe.db.exists("User", mention):
                mentioned_users.append(mention)
        
        return mentioned_users

    def get_hashtags(self):
        """Get hashtags from content"""
        hashtags = []
        content = self.content
        
        # Find #hashtags in content
        import re
        hashtags = re.findall(r'#(\w+)', content)
        
        return hashtags

    def generate_recommendations(self):
        """Generate moment recommendations"""
        recommendations = []
        
        # Content recommendations
        if len(self.content) < 50:
            recommendations.append("Consider adding more detail to your post")
        
        # Engagement recommendations
        if self.likes_count < 5:
            recommendations.append("Consider engaging with other users to increase visibility")
        
        # Hashtag recommendations
        if not self.get_hashtags():
            recommendations.append("Consider adding relevant hashtags to increase reach")
        
        return recommendations

    def update_moment_analytics(self):
        """Update moment analytics"""
        # Update moment analytics data
        analytics_data = {
            "analytics_name": f"Moment Analytics - {self.moment_id}",
            "analytics_type": "Moment Analytics",
            "metrics": {
                "moment_id": self.moment_id,
                "user": self.user,
                "moment_type": self.moment_type,
                "likes_count": self.likes_count or 0,
                "comments_count": self.comments_count or 0,
                "shares_count": self.shares_count or 0,
                "visibility": self.visibility,
                "status": self.status
            },
            "insights": self.generate_moment_insights(),
            "last_updated": now()
        }
        
        # Update or create Moment Analytics DocType
        if frappe.db.exists("Moment Analytics", self.moment_id):
            moment_analytics = frappe.get_doc("Moment Analytics", self.moment_id)
            moment_analytics.update(analytics_data)
            moment_analytics.save(ignore_permissions=True)
        else:
            moment_analytics = frappe.new_doc("Moment Analytics")
            moment_analytics.update(analytics_data)
            moment_analytics.name = self.moment_id
            moment_analytics.insert(ignore_permissions=True)

    def sync_moment_data(self):
        """Sync moment data across systems"""
        # Sync with external social media systems if configured
        if self.external_system_id:
            self.sync_with_external_system()

    def process_moment_changes(self):
        """Process moment changes"""
        # Log changes
        self.log_moment_changes()
        
        # Update related records
        self.update_related_records()
        
        # Trigger notifications
        self.trigger_change_notifications()

    def log_moment_changes(self):
        """Log moment changes"""
        frappe.get_doc({
            "doctype": "Moment Change Log",
            "moment": self.name,
            "changed_by": frappe.session.user,
            "change_date": now(),
            "description": f"Moment {self.moment_id} updated"
        }).insert(ignore_permissions=True)

    def update_related_records(self):
        """Update related records"""
        # Update user activity records
        self.update_user_activity_records()

    def update_user_activity_records(self):
        """Update user activity records"""
        # Update user activity summary
        frappe.db.sql("""
            UPDATE `tabUser`
            SET last_activity_date = %s,
                total_moments = (
                    SELECT COUNT(*) FROM `tabMoment`
                    WHERE user = %s AND status = 'Active'
                )
            WHERE name = %s
        """, (self.moment_date, self.user, self.user))

    def trigger_change_notifications(self):
        """Trigger change notifications"""
        # Notify followers
        self.notify_followers()
        
        # Notify mentioned users
        self.notify_mentioned_users()

    def notify_followers(self):
        """Notify followers"""
        # Get user followers
        followers = frappe.get_list("User Follow",
            filters={"following": self.user},
            fields=["follower"]
        )
        
        for follower in followers:
            frappe.get_doc({
                "doctype": "Moment Notification",
                "moment": self.name,
                "notification_type": "New Moment",
                "message": f"New moment from {self.user}",
                "recipients": follower.follower,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def notify_mentioned_users(self):
        """Notify mentioned users"""
        mentioned_users = self.get_mentioned_users()
        
        for user in mentioned_users:
            frappe.get_doc({
                "doctype": "Moment Notification",
                "moment": self.name,
                "notification_type": "Mention",
                "message": f"You were mentioned in a moment by {self.user}",
                "recipients": user,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def sync_with_external_system(self):
        """Sync moment data with external system"""
        # Implementation for external system sync
        pass

    @frappe.whitelist()
    def get_moment_dashboard_data(self):
        """Get moment dashboard data"""
        return {
            "moment_id": self.moment_id,
            "user": self.user,
            "content": self.content,
            "moment_type": self.moment_type,
            "visibility": self.visibility,
            "status": self.status,
            "likes_count": self.likes_count or 0,
            "comments_count": self.comments_count or 0,
            "shares_count": self.shares_count or 0,
            "location": self.location,
            "mentioned_users": self.get_mentioned_users(),
            "hashtags": self.get_hashtags(),
            "insights": self.generate_moment_insights()
        }

    @frappe.whitelist()
    def like_moment(self, user):
        """Like moment"""
        # Check if user already liked
        existing_like = frappe.get_list("Moment Like",
            filters={"moment": self.name, "user": user},
            fields=["name"]
        )
        
        if existing_like:
            frappe.throw(_("User has already liked this moment"))
        
        # Create like entry
        like = frappe.new_doc("Moment Like")
        like.moment = self.name
        like.user = user
        like.like_date = now()
        like.save(ignore_permissions=True)
        
        # Update likes count
        self.likes_count = (self.likes_count or 0) + 1
        self.save()
        
        frappe.msgprint(_("Moment liked by {0}").format(user))
        return self.as_dict()

    @frappe.whitelist()
    def comment_moment(self, user, comment):
        """Comment on moment"""
        # Create comment entry
        comment_doc = frappe.new_doc("Moment Comment")
        comment_doc.moment = self.name
        comment_doc.user = user
        comment_doc.comment = comment
        comment_doc.comment_date = now()
        comment_doc.save(ignore_permissions=True)
        
        # Update comments count
        self.comments_count = (self.comments_count or 0) + 1
        self.save()
        
        frappe.msgprint(_("Comment added to moment"))
        return self.as_dict()

    @frappe.whitelist()
    def share_moment(self, user):
        """Share moment"""
        # Create share entry
        share = frappe.new_doc("Moment Share")
        share.moment = self.name
        share.user = user
        share.share_date = now()
        share.save(ignore_permissions=True)
        
        # Update shares count
        self.shares_count = (self.shares_count or 0) + 1
        self.save()
        
        frappe.msgprint(_("Moment shared by {0}").format(user))
        return self.as_dict()