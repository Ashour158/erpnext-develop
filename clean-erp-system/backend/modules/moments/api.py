# Moments API - Complete Social and Collaboration Platform API
# Advanced social operations without Frappe dependencies

from flask import Blueprint, request, jsonify
from core.database import db
from core.auth import token_required, get_current_user
from .models import (
    Moment, MomentReaction, MomentComment, MomentShare, MomentTag,
    UserFeed, Notification, Follow, UserProfile, MomentCategory
)
from datetime import datetime, date, timedelta
import json

moments_api = Blueprint('moments_api', __name__)

# User Profile Management
@moments_api.route('/user-profiles', methods=['GET'])
@token_required
def get_user_profiles():
    """Get user profiles"""
    try:
        company_id = request.args.get('company_id')
        user_id = request.args.get('user_id')
        
        query = UserProfile.query.filter_by(company_id=company_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        profiles = query.all()
        return jsonify({
            'success': True,
            'data': [profile.to_dict() for profile in profiles]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/user-profiles', methods=['POST'])
@token_required
def create_user_profile():
    """Create user profile"""
    try:
        data = request.get_json()
        profile = UserProfile(
            user_id=data['user_id'],
            display_name=data.get('display_name'),
            bio=data.get('bio'),
            profile_picture=data.get('profile_picture'),
            cover_photo=data.get('cover_photo'),
            website=data.get('website'),
            location=data.get('location'),
            birth_date=datetime.fromisoformat(data['birth_date']).date() if data.get('birth_date') else None,
            is_public=data.get('is_public', True),
            allow_following=data.get('allow_following', True),
            allow_messages=data.get('allow_messages', True),
            company_id=data['company_id']
        )
        db.session.add(profile)
        db.session.commit()
        return jsonify({'success': True, 'data': profile.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/user-profiles/<int:profile_id>', methods=['PUT'])
@token_required
def update_user_profile(profile_id):
    """Update user profile"""
    try:
        data = request.get_json()
        profile = UserProfile.query.get_or_404(profile_id)
        
        # Update profile fields
        for field in ['display_name', 'bio', 'profile_picture', 'cover_photo', 
                      'website', 'location', 'is_public', 'allow_following', 'allow_messages']:
            if field in data:
                setattr(profile, field, data[field])
        
        if 'birth_date' in data and data['birth_date']:
            profile.birth_date = datetime.fromisoformat(data['birth_date']).date()
        
        db.session.commit()
        return jsonify({'success': True, 'data': profile.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Moment Category Management
@moments_api.route('/moment-categories', methods=['GET'])
@token_required
def get_moment_categories():
    """Get moment categories"""
    try:
        company_id = request.args.get('company_id')
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        
        query = MomentCategory.query.filter_by(company_id=company_id)
        if is_active:
            query = query.filter_by(is_active=True)
        
        categories = query.all()
        return jsonify({
            'success': True,
            'data': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/moment-categories', methods=['POST'])
@token_required
def create_moment_category():
    """Create moment category"""
    try:
        data = request.get_json()
        category = MomentCategory(
            category_name=data['category_name'],
            category_code=data['category_code'],
            description=data.get('description'),
            color=data.get('color', '#007bff'),
            icon=data.get('icon'),
            is_active=data.get('is_active', True),
            is_default=data.get('is_default', False),
            company_id=data['company_id']
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'success': True, 'data': category.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Moment Management
@moments_api.route('/moments', methods=['GET'])
@token_required
def get_moments():
    """Get moments"""
    try:
        company_id = request.args.get('company_id')
        author_id = request.args.get('author_id')
        category_id = request.args.get('category_id')
        moment_type = request.args.get('moment_type')
        visibility = request.args.get('visibility')
        is_featured = request.args.get('is_featured')
        is_announcement = request.args.get('is_announcement')
        
        query = Moment.query.filter_by(company_id=company_id, is_published=True)
        if author_id:
            query = query.filter_by(author_id=author_id)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if moment_type:
            query = query.filter_by(moment_type=moment_type)
        if visibility:
            query = query.filter_by(visibility=visibility)
        if is_featured:
            query = query.filter_by(is_featured=is_featured.lower() == 'true')
        if is_announcement:
            query = query.filter_by(is_announcement=is_announcement.lower() == 'true')
        
        # Order by creation date (newest first)
        query = query.order_by(Moment.created_at.desc())
        
        moments = query.all()
        return jsonify({
            'success': True,
            'data': [moment.to_dict() for moment in moments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/moments', methods=['POST'])
@token_required
def create_moment():
    """Create moment"""
    try:
        data = request.get_json()
        moment = Moment(
            author_id=data['author_id'],
            author_profile_id=data.get('author_profile_id'),
            content=data['content'],
            moment_type=data.get('moment_type', 'Text'),
            visibility=data.get('visibility', 'Public'),
            media_urls=data.get('media_urls', []),
            media_type=data.get('media_type'),
            category_id=data.get('category_id'),
            tags=data.get('tags', []),
            mentions=data.get('mentions', []),
            location=data.get('location'),
            mood=data.get('mood'),
            poll_question=data.get('poll_question'),
            poll_options=data.get('poll_options', []),
            poll_end_date=datetime.fromisoformat(data['poll_end_date']) if data.get('poll_end_date') else None,
            is_featured=data.get('is_featured', False),
            is_announcement=data.get('is_announcement', False),
            company_id=data['company_id']
        )
        db.session.add(moment)
        db.session.commit()
        
        # Create tags if provided
        if data.get('tags'):
            for tag_name in data['tags']:
                tag = MomentTag(
                    moment_id=moment.id,
                    tag_name=tag_name,
                    company_id=data['company_id']
                )
                db.session.add(tag)
        
        db.session.commit()
        return jsonify({'success': True, 'data': moment.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/moments/<int:moment_id>', methods=['GET'])
@token_required
def get_moment(moment_id):
    """Get specific moment"""
    try:
        moment = Moment.query.get_or_404(moment_id)
        return jsonify({'success': True, 'data': moment.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/moments/<int:moment_id>/like', methods=['POST'])
@token_required
def like_moment(moment_id):
    """Like/unlike moment"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        reaction_type = data.get('reaction_type', 'Like')
        
        # Check if user already reacted
        existing_reaction = MomentReaction.query.filter_by(
            moment_id=moment_id, user_id=user_id
        ).first()
        
        if existing_reaction:
            # Remove existing reaction
            db.session.delete(existing_reaction)
            # Update moment likes count
            moment = Moment.query.get(moment_id)
            if moment:
                moment.likes_count = max(0, moment.likes_count - 1)
        else:
            # Add new reaction
            reaction = MomentReaction(
                moment_id=moment_id,
                user_id=user_id,
                reaction_type=reaction_type,
                company_id=data['company_id']
            )
            db.session.add(reaction)
            # Update moment likes count
            moment = Moment.query.get(moment_id)
            if moment:
                moment.likes_count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'data': moment.to_dict() if moment else {}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Moment Comments
@moments_api.route('/moments/<int:moment_id>/comments', methods=['GET'])
@token_required
def get_moment_comments(moment_id):
    """Get moment comments"""
    try:
        comments = MomentComment.query.filter_by(moment_id=moment_id).all()
        return jsonify({
            'success': True,
            'data': [comment.to_dict() for comment in comments]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/moments/<int:moment_id>/comments', methods=['POST'])
@token_required
def create_moment_comment(moment_id):
    """Create moment comment"""
    try:
        data = request.get_json()
        comment = MomentComment(
            moment_id=moment_id,
            user_id=data['user_id'],
            content=data['content'],
            parent_comment_id=data.get('parent_comment_id'),
            company_id=data['company_id']
        )
        db.session.add(comment)
        
        # Update moment comments count
        moment = Moment.query.get(moment_id)
        if moment:
            moment.comments_count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'data': comment.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Moment Shares
@moments_api.route('/moments/<int:moment_id>/share', methods=['POST'])
@token_required
def share_moment(moment_id):
    """Share moment"""
    try:
        data = request.get_json()
        share = MomentShare(
            moment_id=moment_id,
            user_id=data['user_id'],
            share_text=data.get('share_text'),
            share_visibility=data.get('share_visibility', 'Public'),
            company_id=data['company_id']
        )
        db.session.add(share)
        
        # Update moment shares count
        moment = Moment.query.get(moment_id)
        if moment:
            moment.shares_count += 1
        
        db.session.commit()
        return jsonify({'success': True, 'data': share.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Follow Management
@moments_api.route('/follow', methods=['POST'])
@token_required
def follow_user():
    """Follow user"""
    try:
        data = request.get_json()
        follower_id = data['follower_id']
        followed_id = data['followed_id']
        
        # Check if already following
        existing_follow = Follow.query.filter_by(
            follower_id=follower_id, followed_id=followed_id
        ).first()
        
        if existing_follow:
            # Toggle follow status
            existing_follow.is_active = not existing_follow.is_active
        else:
            # Create new follow
            follow = Follow(
                follower_id=follower_id,
                followed_id=followed_id,
                company_id=data['company_id']
            )
            db.session.add(follow)
        
        db.session.commit()
        return jsonify({'success': True, 'data': {'followed': existing_follow.is_active if existing_follow else True}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/users/<int:user_id>/followers', methods=['GET'])
@token_required
def get_user_followers(user_id):
    """Get user followers"""
    try:
        followers = Follow.query.filter_by(followed_id=user_id, is_active=True).all()
        return jsonify({
            'success': True,
            'data': [follow.to_dict() for follow in followers]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/users/<int:user_id>/following', methods=['GET'])
@token_required
def get_user_following(user_id):
    """Get user following"""
    try:
        following = Follow.query.filter_by(follower_id=user_id, is_active=True).all()
        return jsonify({
            'success': True,
            'data': [follow.to_dict() for follow in following]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# User Feed
@moments_api.route('/users/<int:user_id>/feed', methods=['GET'])
@token_required
def get_user_feed(user_id):
    """Get user feed"""
    try:
        feed_type = request.args.get('feed_type', 'following')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Get feed moments
        feed_query = UserFeed.query.filter_by(user_id=user_id, feed_type=feed_type)
        feed_query = feed_query.order_by(UserFeed.feed_score.desc()).limit(limit).offset(offset)
        
        feed_items = feed_query.all()
        moments = [item.moment.to_dict() for item in feed_items]
        
        return jsonify({
            'success': True,
            'data': moments
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Notifications
@moments_api.route('/users/<int:user_id>/notifications', methods=['GET'])
@token_required
def get_user_notifications(user_id):
    """Get user notifications"""
    try:
        is_read = request.args.get('is_read')
        notification_type = request.args.get('notification_type')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        query = Notification.query.filter_by(user_id=user_id)
        if is_read is not None:
            query = query.filter_by(is_read=is_read.lower() == 'true')
        if notification_type:
            query = query.filter_by(notification_type=notification_type)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        notifications = query.all()
        
        return jsonify({
            'success': True,
            'data': [notification.to_dict() for notification in notifications]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@moments_api.route('/notifications/<int:notification_id>/read', methods=['POST'])
@token_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        notification.is_read = True
        notification.read_date = datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'data': notification.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Social Analytics
@moments_api.route('/social-analytics', methods=['GET'])
@token_required
def get_social_analytics():
    """Get social analytics"""
    try:
        company_id = request.args.get('company_id')
        user_id = request.args.get('user_id')
        
        # Calculate analytics
        total_moments = Moment.query.filter_by(company_id=company_id).count()
        total_users = UserProfile.query.filter_by(company_id=company_id).count()
        total_follows = Follow.query.filter_by(company_id=company_id, is_active=True).count()
        
        if user_id:
            user_moments = Moment.query.filter_by(company_id=company_id, author_id=user_id).count()
            user_followers = Follow.query.filter_by(company_id=company_id, followed_id=user_id, is_active=True).count()
            user_following = Follow.query.filter_by(company_id=company_id, follower_id=user_id, is_active=True).count()
            
            analytics = {
                'user_moments': user_moments,
                'user_followers': user_followers,
                'user_following': user_following
            }
        else:
            analytics = {
                'total_moments': total_moments,
                'total_users': total_users,
                'total_follows': total_follows,
                'engagement_rate': (total_follows / total_users * 100) if total_users > 0 else 0
            }
        
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
