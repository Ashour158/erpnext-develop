# Moments Models - Complete Social and Collaboration Platform
# Advanced social models without Frappe dependencies

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Enums
class MomentType(enum.Enum):
    TEXT = "Text"
    IMAGE = "Image"
    VIDEO = "Video"
    LINK = "Link"
    POLL = "Poll"
    ANNOUNCEMENT = "Announcement"

class MomentVisibility(enum.Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"
    FOLLOWERS = "Followers"
    TEAM = "Team"
    COMPANY = "Company"

class ReactionType(enum.Enum):
    LIKE = "Like"
    LOVE = "Love"
    LAUGH = "Laugh"
    WOW = "Wow"
    SAD = "Sad"
    ANGRY = "Angry"

class NotificationType(enum.Enum):
    MOMENT_LIKE = "Moment Like"
    MOMENT_COMMENT = "Moment Comment"
    MOMENT_SHARE = "Moment Share"
    NEW_FOLLOWER = "New Follower"
    MENTION = "Mention"
    ANNOUNCEMENT = "Announcement"

# Moment Category Model
class MomentCategory(BaseModel):
    """Moment Category model"""
    __tablename__ = 'moment_categories'
    
    category_name = db.Column(db.String(200), nullable=False)
    category_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # Hex color
    icon = db.Column(db.String(100))
    
    # Category Settings
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    moments = relationship("Moment", back_populates="category")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'category_name': self.category_name,
            'category_code': self.category_code,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'company_id': self.company_id
        })
        return data

# User Profile Model
class UserProfile(BaseModel):
    """User Profile model"""
    __tablename__ = 'user_profiles'
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Profile Details
    display_name = db.Column(db.String(200))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))
    cover_photo = db.Column(db.String(255))
    
    # Social Information
    website = db.Column(db.String(200))
    location = db.Column(db.String(200))
    birth_date = db.Column(db.Date)
    
    # Privacy Settings
    is_public = db.Column(db.Boolean, default=True)
    allow_following = db.Column(db.Boolean, default=True)
    allow_messages = db.Column(db.Boolean, default=True)
    
    # Statistics
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    moments_count = db.Column(db.Integer, default=0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    moments = relationship("Moment", back_populates="author_profile")
    followers = relationship("Follow", back_populates="followed_profile", foreign_keys="Follow.followed_id")
    following = relationship("Follow", back_populates="follower_profile", foreign_keys="Follow.follower_id")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'display_name': self.display_name,
            'bio': self.bio,
            'profile_picture': self.profile_picture,
            'cover_photo': self.cover_photo,
            'website': self.website,
            'location': self.location,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'is_public': self.is_public,
            'allow_following': self.allow_following,
            'allow_messages': self.allow_messages,
            'followers_count': self.followers_count,
            'following_count': self.following_count,
            'moments_count': self.moments_count,
            'company_id': self.company_id
        })
        return data

# Moment Model
class Moment(BaseModel):
    """Moment model"""
    __tablename__ = 'moments'
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    author = relationship("Employee")
    author_profile_id = db.Column(db.Integer, db.ForeignKey('user_profiles.id'))
    author_profile = relationship("UserProfile", back_populates="moments")
    
    # Content
    content = db.Column(db.Text, nullable=False)
    moment_type = db.Column(db.Enum(MomentType), default=MomentType.TEXT)
    visibility = db.Column(db.Enum(MomentVisibility), default=MomentVisibility.PUBLIC)
    
    # Media
    media_urls = db.Column(db.JSON)  # List of media URLs
    media_type = db.Column(db.String(50))  # image, video, audio, etc.
    
    # Category
    category_id = db.Column(db.Integer, db.ForeignKey('moment_categories.id'))
    category = relationship("MomentCategory", back_populates="moments")
    
    # Engagement
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    
    # Additional Information
    tags = db.Column(db.JSON)  # List of tags
    mentions = db.Column(db.JSON)  # List of mentioned users
    location = db.Column(db.String(200))
    mood = db.Column(db.String(50))
    
    # Poll Information (if moment_type is POLL)
    poll_question = db.Column(db.Text)
    poll_options = db.Column(db.JSON)
    poll_end_date = db.Column(db.DateTime)
    poll_votes = db.Column(db.JSON)
    
    # Status
    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_announcement = db.Column(db.Boolean, default=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    # Relationships
    reactions = relationship("MomentReaction", back_populates="moment")
    comments = relationship("MomentComment", back_populates="moment")
    shares = relationship("MomentShare", back_populates="moment")
    moment_tags = relationship("MomentTag", back_populates="moment")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'author_id': self.author_id,
            'author_profile_id': self.author_profile_id,
            'content': self.content,
            'moment_type': self.moment_type.value if self.moment_type else None,
            'visibility': self.visibility.value if self.visibility else None,
            'media_urls': self.media_urls,
            'media_type': self.media_type,
            'category_id': self.category_id,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'views_count': self.views_count,
            'tags': self.tags,
            'mentions': self.mentions,
            'location': self.location,
            'mood': self.mood,
            'poll_question': self.poll_question,
            'poll_options': self.poll_options,
            'poll_end_date': self.poll_end_date.isoformat() if self.poll_end_date else None,
            'poll_votes': self.poll_votes,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'is_announcement': self.is_announcement,
            'company_id': self.company_id
        })
        return data

# Moment Reaction Model
class MomentReaction(BaseModel):
    """Moment Reaction model"""
    __tablename__ = 'moment_reactions'
    
    # Moment
    moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
    moment = relationship("Moment", back_populates="reactions")
    
    # User
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Reaction
    reaction_type = db.Column(db.Enum(ReactionType), nullable=False)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'moment_id': self.moment_id,
            'user_id': self.user_id,
            'reaction_type': self.reaction_type.value if self.reaction_type else None,
            'company_id': self.company_id
        })
        return data

# Moment Comment Model
class MomentComment(BaseModel):
    """Moment Comment model"""
    __tablename__ = 'moment_comments'
    
    # Moment
    moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
    moment = relationship("Moment", back_populates="comments")
    
    # User
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Comment
    content = db.Column(db.Text, nullable=False)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('moment_comments.id'))
    parent_comment = relationship("MomentComment", remote_side=[id])
    replies = relationship("MomentComment", back_populates="parent_comment")
    
    # Engagement
    likes_count = db.Column(db.Integer, default=0)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'moment_id': self.moment_id,
            'user_id': self.user_id,
            'content': self.content,
            'parent_comment_id': self.parent_comment_id,
            'likes_count': self.likes_count,
            'company_id': self.company_id
        })
        return data

# Moment Share Model
class MomentShare(BaseModel):
    """Moment Share model"""
    __tablename__ = 'moment_shares'
    
    # Original Moment
    moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
    moment = relationship("Moment", back_populates="shares")
    
    # User who shared
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Share Details
    share_text = db.Column(db.Text)
    share_visibility = db.Column(db.Enum(MomentVisibility), default=MomentVisibility.PUBLIC)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'moment_id': self.moment_id,
            'user_id': self.user_id,
            'share_text': self.share_text,
            'share_visibility': self.share_visibility.value if self.share_visibility else None,
            'company_id': self.company_id
        })
        return data

# Moment Tag Model
class MomentTag(BaseModel):
    """Moment Tag model"""
    __tablename__ = 'moment_tags'
    
    # Moment
    moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
    moment = relationship("Moment", back_populates="moment_tags")
    
    # Tag
    tag_name = db.Column(db.String(100), nullable=False)
    tag_color = db.Column(db.String(7), default='#007bff')
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'moment_id': self.moment_id,
            'tag_name': self.tag_name,
            'tag_color': self.tag_color,
            'company_id': self.company_id
        })
        return data

# Follow Model
class Follow(BaseModel):
    """Follow model"""
    __tablename__ = 'follows'
    
    # Follower
    follower_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    follower = relationship("Employee", foreign_keys=[follower_id])
    follower_profile_id = db.Column(db.Integer, db.ForeignKey('user_profiles.id'))
    follower_profile = relationship("UserProfile", back_populates="following", foreign_keys=[follower_profile_id])
    
    # Followed User
    followed_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    followed = relationship("Employee", foreign_keys=[followed_id])
    followed_profile_id = db.Column(db.Integer, db.ForeignKey('user_profiles.id'))
    followed_profile = relationship("UserProfile", back_populates="followers", foreign_keys=[followed_profile_id])
    
    # Follow Status
    is_active = db.Column(db.Boolean, default=True)
    follow_date = db.Column(db.DateTime, default=datetime.now)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'follower_id': self.follower_id,
            'follower_profile_id': self.follower_profile_id,
            'followed_id': self.followed_id,
            'followed_profile_id': self.followed_profile_id,
            'is_active': self.is_active,
            'follow_date': self.follow_date.isoformat() if self.follow_date else None,
            'company_id': self.company_id
        })
        return data

# User Feed Model
class UserFeed(BaseModel):
    """User Feed model"""
    __tablename__ = 'user_feeds'
    
    # User
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Moment
    moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
    moment = relationship("Moment")
    
    # Feed Information
    feed_type = db.Column(db.String(50))  # following, trending, company, etc.
    feed_score = db.Column(db.Float, default=0.0)  # For algorithm ranking
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'moment_id': self.moment_id,
            'feed_type': self.feed_type,
            'feed_score': self.feed_score,
            'company_id': self.company_id
        })
        return data

# Notification Model
class Notification(BaseModel):
    """Notification model"""
    __tablename__ = 'notifications'
    
    # User
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Notification Details
    notification_type = db.Column(db.Enum(NotificationType), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Related Objects
    related_moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'))
    related_moment = relationship("Moment")
    related_user_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    related_user = relationship("Employee", foreign_keys=[related_user_id])
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    read_date = db.Column(db.DateTime)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'user_id': self.user_id,
            'notification_type': self.notification_type.value if self.notification_type else None,
            'title': self.title,
            'message': self.message,
            'related_moment_id': self.related_moment_id,
            'related_user_id': self.related_user_id,
            'is_read': self.is_read,
            'read_date': self.read_date.isoformat() if self.read_date else None,
            'company_id': self.company_id
        })
        return data
