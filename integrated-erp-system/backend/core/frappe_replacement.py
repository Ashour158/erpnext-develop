# Frappe Replacement Functions
# Complete replacement for all Frappe framework functionality

import json
import uuid
import hashlib
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union
from .database_manager import db, get_list, get_value, set_value, exists, count, sql

# User Management
def get_current_user():
    """Get current user from session"""
    # This would be implemented based on your authentication system
    return "Administrator"  # Default for now

def get_user(user_id=None):
    """Get user information"""
    if not user_id:
        user_id = get_current_user()
    
    return get_value("User", "*", {"name": user_id})

# Document Management
class Document:
    """Document class to replace frappe.get_doc()"""
    
    def __init__(self, doctype, name=None, data=None):
        self.doctype = doctype
        self.name = name
        self.data = data or {}
        self.is_new = not name
        
        if not self.is_new:
            self.load()
    
    def load(self):
        """Load document from database"""
        if self.name:
            self.data = get_value(self.doctype, "*", {"name": self.name})
            if not self.data:
                raise ValueError(f"Document {self.doctype} {self.name} not found")
    
    def save(self):
        """Save document to database"""
        if self.is_new:
            self.name = str(uuid.uuid4())
            self.data['name'] = self.name
            self.data['creation'] = datetime.now()
            self.data['modified'] = datetime.now()
            db.insert(self.doctype, self.data)
        else:
            self.data['modified'] = datetime.now()
            db.update(self.doctype, self.data, "name = ?", (self.name,))
    
    def delete(self):
        """Delete document"""
        if self.name:
            db.delete(self.doctype, "name = ?", (self.name,))
    
    def get(self, field):
        """Get field value"""
        return self.data.get(field)
    
    def set(self, field, value):
        """Set field value"""
        self.data[field] = value
    
    def __getattr__(self, name):
        """Allow attribute access to document fields"""
        return self.data.get(name)
    
    def __setattr__(self, name, value):
        """Allow attribute setting for document fields"""
        if name in ['doctype', 'name', 'data', 'is_new']:
            super().__setattr__(name, value)
        else:
            if not hasattr(self, 'data'):
                super().__setattr__(name, value)
            else:
                self.data[name] = value

def get_doc(doctype, name=None, data=None):
    """Get document instance"""
    return Document(doctype, name, data)

def new_doc(doctype):
    """Create new document"""
    return Document(doctype)

# Date and Time Functions
def get_date(date_string):
    """Convert string to date object"""
    if isinstance(date_string, date):
        return date_string
    if isinstance(date_string, datetime):
        return date_string.date()
    if isinstance(date_string, str):
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except:
            return datetime.now().date()
    return datetime.now().date()

def format_date(date_obj, format_string='%Y-%m-%d'):
    """Format date object to string"""
    if isinstance(date_obj, str):
        return date_obj
    if isinstance(date_obj, date):
        return date_obj.strftime(format_string)
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_string)
    return datetime.now().strftime(format_string)

# Validation Functions
def validate(condition, message):
    """Validate condition and throw error if false"""
    if not condition:
        throw(message)

def throw(message, title="Error"):
    """Throw validation error"""
    raise ValueError(f"{title}: {message}")

def msgprint(message, title="Message", alert=False):
    """Print message"""
    print(f"{title}: {message}")

# Permission Functions
def has_permission(doctype, permission="read", user=None):
    """Check user permission"""
    if not user:
        user = get_current_user()
    
    # Simple permission check - can be enhanced
    if user == "Administrator":
        return True
    
    # Check user roles and permissions
    user_roles = get_value("User", "roles", {"name": user}) or []
    if "System Manager" in user_roles:
        return True
    
    return False

# Cache Functions
class Cache:
    """Simple cache implementation"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        """Get from cache"""
        return self.cache.get(key)
    
    def set(self, key, value, expires_in=None):
        """Set cache value"""
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=expires_in) if expires_in else None
        }
    
    def delete(self, key):
        """Delete from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()

cache = Cache()

# Queue Functions
def enqueue(method, queue="default", timeout=None, **kwargs):
    """Enqueue method for background execution"""
    # Simple implementation - can be enhanced with proper queue system
    try:
        if hasattr(method, '__call__'):
            method(**kwargs)
        else:
            # If method is string, try to import and call
            module_name, func_name = method.rsplit('.', 1)
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            func(**kwargs)
    except Exception as e:
        print(f"Queue execution error: {str(e)}")

# Email Functions
def sendmail(recipients, subject, message, attachments=None, cc=None, bcc=None):
    """Send email"""
    # Simple email implementation - can be enhanced with proper email service
    print(f"Email to {recipients}: {subject}")
    print(f"Message: {message}")
    if attachments:
        print(f"Attachments: {attachments}")

# File Functions
def get_file_path(file_name):
    """Get file path"""
    return f"files/{file_name}"

def get_attached_files(doctype, name):
    """Get attached files for document"""
    return get_list("File", filters={"attached_to_doctype": doctype, "attached_to_name": name})

# Translation Functions
def _(text):
    """Translation function"""
    return text  # Simple implementation - can be enhanced with proper i18n

def translate(text, language=None):
    """Translate text"""
    return text  # Simple implementation

# System Functions
def get_meta(doctype):
    """Get document meta information"""
    return {
        'name': doctype,
        'fields': get_list("DocField", filters={"parent": doctype}),
        'permissions': get_list("DocPerm", filters={"parent": doctype})
    }

def get_system_settings():
    """Get system settings"""
    return get_value("System Settings", "*", {"name": "System Settings"})

def get_site_config():
    """Get site configuration"""
    return {
        'db_name': 'erp_system',
        'db_type': 'sqlite',
        'encryption_key': 'default_key'
    }

# Hook Functions
def hooks():
    """Get hooks"""
    return {}

def events():
    """Get events"""
    return {}

# Utility Functions
def cstr(value):
    """Convert to string"""
    return str(value) if value is not None else ""

def cint(value):
    """Convert to integer"""
    try:
        return int(value) if value is not None else 0
    except:
        return 0

def cfloat(value):
    """Convert to float"""
    try:
        return float(value) if value is not None else 0.0
    except:
        return 0.0

def flt(value):
    """Convert to float"""
    return cfloat(value)

# Additional utility functions
def get_file_size(file_path):
    """Get file size"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def get_file_extension(file_path):
    """Get file extension"""
    return os.path.splitext(file_path)[1]

def generate_hash(text):
    """Generate hash for text"""
    return hashlib.md5(text.encode()).hexdigest()

def generate_uuid():
    """Generate UUID"""
    return str(uuid.uuid4())

def make_autoname(pattern):
    """Generate autoname based on pattern"""
    import re
    from datetime import datetime
    
    # Replace pattern placeholders
    pattern = pattern.replace('.YYYY.', str(datetime.now().year))
    pattern = pattern.replace('.MM.', str(datetime.now().month).zfill(2))
    pattern = pattern.replace('.DD.', str(datetime.now().day).zfill(2))
    
    # Replace ##### with random number
    if '#####' in pattern:
        import random
        pattern = pattern.replace('#####', str(random.randint(10000, 99999)))
    
    return pattern

def add_days(date_obj, days):
    """Add days to date"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    return date_obj + timedelta(days=days)

def get_datetime(date_string):
    """Convert string to datetime"""
    if isinstance(date_string, datetime):
        return date_string
    if isinstance(date_string, str):
        try:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.strptime(date_string, '%Y-%m-%d')
    return datetime.now()

def get_time(time_string):
    """Get time from string"""
    if isinstance(time_string, str):
        try:
            return datetime.strptime(time_string, '%H:%M:%S').time()
        except:
            return datetime.strptime(time_string, '%H:%M').time()
    return datetime.now().time()

def date_diff(date1, date2):
    """Calculate difference between dates"""
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, '%Y-%m-%d').date()
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, '%Y-%m-%d').date()
    return (date1 - date2).days

def copy_doc(doc):
    """Copy document"""
    new_doc = Document(doc.doctype)
    new_doc.data = doc.data.copy()
    new_doc.name = None
    new_doc.is_new = True
    return new_doc

# Import all functions to make them available
__all__ = [
    'get_current_user', 'get_user', 'Document', 'get_doc', 'new_doc',
    'get_date', 'format_date', 'validate', 'throw', 'msgprint',
    'has_permission', 'cache', 'enqueue', 'sendmail', 'get_file_path',
    'get_attached_files', '_', 'translate', 'get_meta', 'get_system_settings',
    'get_site_config', 'hooks', 'events', 'cstr', 'cint', 'cfloat', 'flt',
    'get_file_size', 'get_file_extension', 'generate_hash', 'generate_uuid',
    'make_autoname', 'add_days', 'get_datetime', 'get_time', 'date_diff', 'copy_doc'
]
