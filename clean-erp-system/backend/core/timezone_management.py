# Timezone Management System
# Timezone-aware scheduling and event management

from core.database import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime, time, timedelta
import enum
import pytz
from typing import Dict, List, Optional, Tuple
import json

class TimezoneStatus(enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DISABLED = "Disabled"

class TimezoneRule(BaseModel):
    """Timezone rule model"""
    __tablename__ = 'timezone_rules'
    
    # Rule Information
    rule_name = db.Column(db.String(200), nullable=False)
    rule_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timezone Information
    timezone = db.Column(db.String(50), nullable=False)  # e.g., 'America/New_York'
    timezone_display = db.Column(db.String(100))  # e.g., 'Eastern Time (US & Canada)'
    utc_offset = db.Column(db.Float, default=0.0)  # hours from UTC
    dst_offset = db.Column(db.Float, default=0.0)  # DST offset in hours
    
    # DST Rules
    dst_start_rule = db.Column(db.JSON)  # DST start rule
    dst_end_rule = db.Column(db.JSON)  # DST end rule
    dst_enabled = db.Column(db.Boolean, default=True)
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'rule_name': self.rule_name,
            'rule_description': self.rule_description,
            'is_active': self.is_active,
            'timezone': self.timezone,
            'timezone_display': self.timezone_display,
            'utc_offset': self.utc_offset,
            'dst_offset': self.dst_offset,
            'dst_start_rule': self.dst_start_rule,
            'dst_end_rule': self.dst_end_rule,
            'dst_enabled': self.dst_enabled,
            'company_id': self.company_id
        })
        return data

class UserTimezone(BaseModel):
    """User timezone model"""
    __tablename__ = 'user_timezones'
    
    # Timezone Information
    timezone = db.Column(db.String(50), nullable=False)
    timezone_display = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=True)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'timezone': self.timezone,
            'timezone_display': self.timezone_display,
            'is_primary': self.is_primary,
            'user_id': self.user_id,
            'company_id': self.company_id
        })
        return data

class TimezoneConversion(BaseModel):
    """Timezone conversion model"""
    __tablename__ = 'timezone_conversions'
    
    # Conversion Information
    source_timezone = db.Column(db.String(50), nullable=False)
    target_timezone = db.Column(db.String(50), nullable=False)
    source_datetime = db.Column(db.DateTime, nullable=False)
    target_datetime = db.Column(db.DateTime, nullable=False)
    conversion_offset = db.Column(db.Float, default=0.0)  # hours difference
    
    # Context Information
    conversion_context = db.Column(db.String(100))  # Event, Meeting, etc.
    conversion_notes = db.Column(db.Text)
    
    # User Information
    user_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    user = relationship("Employee")
    
    # Company Association
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    company = relationship("Company")
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'source_timezone': self.source_timezone,
            'target_timezone': self.target_timezone,
            'source_datetime': self.source_datetime.isoformat() if self.source_datetime else None,
            'target_datetime': self.target_datetime.isoformat() if self.target_datetime else None,
            'conversion_offset': self.conversion_offset,
            'conversion_context': self.conversion_context,
            'conversion_notes': self.conversion_notes,
            'user_id': self.user_id,
            'company_id': self.company_id
        })
        return data

# Utility Functions
def get_timezone_info(timezone_name: str) -> Dict:
    """Get timezone information"""
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        
        return {
            'timezone': timezone_name,
            'display_name': tz.zone,
            'utc_offset': now.utcoffset().total_seconds() / 3600,
            'dst_offset': now.dst().total_seconds() / 3600 if now.dst() else 0,
            'is_dst': now.dst() is not None,
            'current_time': now.isoformat()
        }
    except Exception as e:
        return {'error': str(e)}

def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert datetime from one timezone to another"""
    try:
        # Get source timezone
        source_tz = pytz.timezone(from_tz)
        
        # Get target timezone
        target_tz = pytz.timezone(to_tz)
        
        # Convert datetime
        if dt.tzinfo is None:
            dt = source_tz.localize(dt)
        
        converted_dt = dt.astimezone(target_tz)
        
        return converted_dt
    except Exception as e:
        raise ValueError(f"Error converting timezone: {e}")

def get_available_timezones() -> List[Dict]:
    """Get list of available timezones"""
    timezones = []
    
    for timezone_name in pytz.all_timezones:
        try:
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
            
            timezones.append({
                'timezone': timezone_name,
                'display_name': tz.zone,
                'utc_offset': now.utcoffset().total_seconds() / 3600,
                'dst_offset': now.dst().total_seconds() / 3600 if now.dst() else 0,
                'is_dst': now.dst() is not None
            })
        except Exception:
            continue
    
    return sorted(timezones, key=lambda x: x['utc_offset'])

def get_timezone_by_offset(offset_hours: float) -> List[str]:
    """Get timezones by UTC offset"""
    timezones = []
    
    for timezone_name in pytz.all_timezones:
        try:
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
            current_offset = now.utcoffset().total_seconds() / 3600
            
            if abs(current_offset - offset_hours) < 0.1:  # Within 6 minutes
                timezones.append(timezone_name)
        except Exception:
            continue
    
    return timezones

def get_business_hours(timezone_name: str, start_hour: int = 9, end_hour: int = 17) -> Dict:
    """Get business hours for a timezone"""
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        
        # Get business hours for today
        business_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        business_end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        return {
            'timezone': timezone_name,
            'business_start': business_start.isoformat(),
            'business_end': business_end.isoformat(),
            'is_business_hours': business_start <= now <= business_end,
            'current_time': now.isoformat()
        }
    except Exception as e:
        return {'error': str(e)}

def find_common_business_hours(timezones: List[str], start_hour: int = 9, end_hour: int = 17) -> Dict:
    """Find common business hours across multiple timezones"""
    try:
        business_hours = {}
        
        for tz_name in timezones:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            
            # Get business hours for this timezone
            business_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            business_end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
            
            business_hours[tz_name] = {
                'business_start': business_start.isoformat(),
                'business_end': business_end.isoformat(),
                'utc_offset': now.utcoffset().total_seconds() / 3600
            }
        
        # Find overlapping hours
        # This is a simplified implementation
        # In practice, you'd need more sophisticated logic
        
        return {
            'timezones': business_hours,
            'common_hours': {
                'start': f"{start_hour}:00",
                'end': f"{end_hour}:00"
            }
        }
    except Exception as e:
        return {'error': str(e)}

def schedule_event_across_timezones(event_datetime: datetime, timezones: List[str], duration_hours: float = 1.0) -> Dict:
    """Schedule event across multiple timezones"""
    try:
        scheduled_times = {}
        
        for tz_name in timezones:
            tz = pytz.timezone(tz_name)
            
            # Convert event datetime to this timezone
            if event_datetime.tzinfo is None:
                event_datetime = pytz.UTC.localize(event_datetime)
            
            local_time = event_datetime.astimezone(tz)
            
            scheduled_times[tz_name] = {
                'local_time': local_time.isoformat(),
                'display_time': local_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'utc_offset': local_time.utcoffset().total_seconds() / 3600,
                'is_dst': local_time.dst() is not None
            }
        
        return {
            'event_datetime': event_datetime.isoformat(),
            'duration_hours': duration_hours,
            'scheduled_times': scheduled_times
        }
    except Exception as e:
        return {'error': str(e)}

def get_timezone_aware_datetime(dt: datetime, timezone_name: str) -> datetime:
    """Get timezone-aware datetime"""
    try:
        tz = pytz.timezone(timezone_name)
        
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)
        
        return dt
    except Exception as e:
        raise ValueError(f"Error creating timezone-aware datetime: {e}")

def get_timezone_difference(tz1: str, tz2: str) -> float:
    """Get time difference between two timezones in hours"""
    try:
        tz1_obj = pytz.timezone(tz1)
        tz2_obj = pytz.timezone(tz2)
        
        now = datetime.now()
        dt1 = tz1_obj.localize(now)
        dt2 = tz2_obj.localize(now)
        
        difference = (dt1.utcoffset() - dt2.utcoffset()).total_seconds() / 3600
        
        return difference
    except Exception as e:
        raise ValueError(f"Error calculating timezone difference: {e}")

def is_business_hours(dt: datetime, timezone_name: str, start_hour: int = 9, end_hour: int = 17) -> bool:
    """Check if datetime is within business hours"""
    try:
        tz = pytz.timezone(timezone_name)
        
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)
        
        hour = dt.hour
        return start_hour <= hour < end_hour
    except Exception as e:
        return False

def get_next_business_hour(dt: datetime, timezone_name: str, start_hour: int = 9, end_hour: int = 17) -> datetime:
    """Get next business hour"""
    try:
        tz = pytz.timezone(timezone_name)
        
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        else:
            dt = dt.astimezone(tz)
        
        # If it's already business hours, return the datetime
        if is_business_hours(dt, timezone_name, start_hour, end_hour):
            return dt
        
        # Get next business day
        next_day = dt + timedelta(days=1)
        next_day = next_day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        return next_day
    except Exception as e:
        return dt

def create_timezone_conversion(user_id: int, source_timezone: str, target_timezone: str, 
                              source_datetime: datetime, company_id: int, **kwargs) -> TimezoneConversion:
    """Create timezone conversion record"""
    try:
        # Convert datetime
        target_datetime = convert_timezone(source_datetime, source_timezone, target_timezone)
        
        # Calculate offset
        offset = get_timezone_difference(source_timezone, target_timezone)
        
        # Create conversion record
        conversion = TimezoneConversion(
            source_timezone=source_timezone,
            target_timezone=target_timezone,
            source_datetime=source_datetime,
            target_datetime=target_datetime,
            conversion_offset=offset,
            conversion_context=kwargs.get('conversion_context'),
            conversion_notes=kwargs.get('conversion_notes'),
            user_id=user_id,
            company_id=company_id
        )
        
        db.session.add(conversion)
        db.session.commit()
        
        return conversion
    except Exception as e:
        raise ValueError(f"Error creating timezone conversion: {e}")

def get_user_timezone(user_id: int, company_id: int) -> Optional[str]:
    """Get user's primary timezone"""
    try:
        user_tz = UserTimezone.query.filter(
            UserTimezone.user_id == user_id,
            UserTimezone.company_id == company_id,
            UserTimezone.is_primary == True
        ).first()
        
        return user_tz.timezone if user_tz else None
    except Exception:
        return None

def set_user_timezone(user_id: int, timezone: str, company_id: int, is_primary: bool = True) -> UserTimezone:
    """Set user's timezone"""
    try:
        # Get timezone info
        tz_info = get_timezone_info(timezone)
        if 'error' in tz_info:
            raise ValueError(tz_info['error'])
        
        # Create or update user timezone
        user_tz = UserTimezone.query.filter(
            UserTimezone.user_id == user_id,
            UserTimezone.company_id == company_id,
            UserTimezone.is_primary == True
        ).first()
        
        if user_tz:
            user_tz.timezone = timezone
            user_tz.timezone_display = tz_info['display_name']
        else:
            user_tz = UserTimezone(
                timezone=timezone,
                timezone_display=tz_info['display_name'],
                is_primary=is_primary,
                user_id=user_id,
                company_id=company_id
            )
            db.session.add(user_tz)
        
        db.session.commit()
        
        return user_tz
    except Exception as e:
        raise ValueError(f"Error setting user timezone: {e}")
