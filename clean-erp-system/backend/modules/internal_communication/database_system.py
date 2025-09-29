# Database System
# Notion-like database and table management system

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import time
import re
from pathlib import Path
import hashlib
import hmac
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyType(Enum):
    TITLE = "title"
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"

class ViewType(Enum):
    TABLE = "table"
    BOARD = "board"
    TIMELINE = "timeline"
    CALENDAR = "calendar"
    GALLERY = "gallery"
    LIST = "list"

class FilterType(Enum):
    EQUALS = "equals"
    DOES_NOT_EQUAL = "does_not_equal"
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "does_not_contain"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_THAN_OR_EQUAL_TO = "greater_than_or_equal_to"
    LESS_THAN_OR_EQUAL_TO = "less_than_or_equal_to"
    BEFORE = "before"
    AFTER = "after"
    ON_OR_BEFORE = "on_or_before"
    ON_OR_AFTER = "on_or_after"
    PAST_WEEK = "past_week"
    PAST_MONTH = "past_month"
    PAST_YEAR = "past_year"
    NEXT_WEEK = "next_week"
    NEXT_MONTH = "next_month"
    NEXT_YEAR = "next_year"

class SortDirection(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"

@dataclass
class Property:
    property_id: str
    name: str
    property_type: PropertyType
    description: str = ""
    options: List[str] = field(default_factory=list)
    formula: str = ""
    relation_database_id: str = ""
    relation_property_id: str = ""
    rollup_property: str = ""
    rollup_function: str = ""
    is_required: bool = False
    is_unique: bool = False
    default_value: Any = None

@dataclass
class DatabaseView:
    view_id: str
    name: str
    view_type: ViewType
    database_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    filters: List[Dict[str, Any]] = field(default_factory=list)
    sorts: List[Dict[str, Any]] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    group_by: Optional[str] = None
    is_default: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DatabaseRecord:
    record_id: str
    database_id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_edited_by: str = ""
    is_archived: bool = False

@dataclass
class Database:
    database_id: str
    title: str
    description: str
    workspace_id: str
    page_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    properties: Dict[str, Property] = field(default_factory=dict)
    views: List[DatabaseView] = field(default_factory=list)
    records: List[DatabaseRecord] = field(default_factory=list)
    is_public: bool = False
    permissions: Dict[str, str] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)

class DatabaseSystem:
    """
    Database System
    Notion-like database and table management system
    """
    
    def __init__(self):
        self.databases: Dict[str, Database] = {}
        self.record_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_processing()
        
        # Initialize default properties
        self._initialize_default_properties()
    
    def _start_processing(self):
        """Start background processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_records, daemon=True)
        thread.start()
        
        logger.info("Database system processing started")
    
    def _process_records(self):
        """Process records in background"""
        while self.is_processing:
            try:
                record_data = self.record_queue.get(timeout=1)
                self._handle_record_processing(record_data)
                self.record_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing record: {str(e)}")
    
    def _initialize_default_properties(self):
        """Initialize default database properties"""
        self.default_properties = {
            PropertyType.TITLE: {
                'name': 'Title',
                'description': 'The main title of the record',
                'is_required': True,
                'is_unique': True
            },
            PropertyType.CREATED_TIME: {
                'name': 'Created Time',
                'description': 'When the record was created',
                'is_required': True
            },
            PropertyType.CREATED_BY: {
                'name': 'Created By',
                'description': 'Who created the record',
                'is_required': True
            },
            PropertyType.LAST_EDITED_TIME: {
                'name': 'Last Edited Time',
                'description': 'When the record was last edited',
                'is_required': True
            },
            PropertyType.LAST_EDITED_BY: {
                'name': 'Last Edited By',
                'description': 'Who last edited the record',
                'is_required': True
            }
        }
    
    def create_database(self, title: str, description: str, workspace_id: str,
                       page_id: str, created_by: str, properties: List[Dict[str, Any]] = None) -> Database:
        """Create a new database"""
        try:
            database = Database(
                database_id=str(uuid.uuid4()),
                title=title,
                description=description,
                workspace_id=workspace_id,
                page_id=page_id,
                created_by=created_by,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add default properties
            self._add_default_properties(database)
            
            # Add custom properties
            if properties:
                for prop_data in properties:
                    self._add_property_to_database(database, prop_data)
            
            # Create default table view
            self._create_default_view(database)
            
            self.databases[database.database_id] = database
            
            logger.info(f"Database created: {database.database_id}")
            return database
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise
    
    def add_property(self, database_id: str, property_data: Dict[str, Any], user_id: str) -> Property:
        """Add a property to a database"""
        try:
            if database_id not in self.databases:
                return None
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return None
            
            property_obj = Property(
                property_id=str(uuid.uuid4()),
                name=property_data['name'],
                property_type=PropertyType(property_data['type']),
                description=property_data.get('description', ''),
                options=property_data.get('options', []),
                formula=property_data.get('formula', ''),
                relation_database_id=property_data.get('relation_database_id', ''),
                relation_property_id=property_data.get('relation_property_id', ''),
                rollup_property=property_data.get('rollup_property', ''),
                rollup_function=property_data.get('rollup_function', ''),
                is_required=property_data.get('is_required', False),
                is_unique=property_data.get('is_unique', False),
                default_value=property_data.get('default_value')
            )
            
            database.properties[property_obj.property_id] = property_obj
            database.updated_at = datetime.now()
            
            logger.info(f"Property added: {property_obj.property_id}")
            return property_obj
            
        except Exception as e:
            logger.error(f"Error adding property: {str(e)}")
            return None
    
    def update_property(self, database_id: str, property_id: str, updates: Dict[str, Any], user_id: str) -> bool:
        """Update a property"""
        try:
            if database_id not in self.databases:
                return False
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return False
            
            if property_id not in database.properties:
                return False
            
            property_obj = database.properties[property_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(property_obj, field):
                    setattr(property_obj, field, value)
            
            database.updated_at = datetime.now()
            
            logger.info(f"Property updated: {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating property: {str(e)}")
            return False
    
    def delete_property(self, database_id: str, property_id: str, user_id: str) -> bool:
        """Delete a property"""
        try:
            if database_id not in self.databases:
                return False
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return False
            
            if property_id not in database.properties:
                return False
            
            # Check if it's a required property
            property_obj = database.properties[property_id]
            if property_obj.is_required:
                return False
            
            # Remove from all records
            for record in database.records:
                if property_id in record.properties:
                    del record.properties[property_id]
            
            # Remove from database
            del database.properties[property_id]
            database.updated_at = datetime.now()
            
            logger.info(f"Property deleted: {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting property: {str(e)}")
            return False
    
    def create_view(self, database_id: str, name: str, view_type: ViewType, user_id: str,
                   filters: List[Dict[str, Any]] = None, sorts: List[Dict[str, Any]] = None,
                   properties: List[str] = None, group_by: str = None) -> DatabaseView:
        """Create a new database view"""
        try:
            if database_id not in self.databases:
                return None
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return None
            
            view = DatabaseView(
                view_id=str(uuid.uuid4()),
                name=name,
                view_type=view_type,
                database_id=database_id,
                created_by=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                filters=filters or [],
                sorts=sorts or [],
                properties=properties or [],
                group_by=group_by
            )
            
            database.views.append(view)
            database.updated_at = datetime.now()
            
            logger.info(f"View created: {view.view_id}")
            return view
            
        except Exception as e:
            logger.error(f"Error creating view: {str(e)}")
            return None
    
    def add_record(self, database_id: str, properties: Dict[str, Any], user_id: str) -> DatabaseRecord:
        """Add a record to a database"""
        try:
            if database_id not in self.databases:
                return None
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return None
            
            # Validate properties
            if not self._validate_record_properties(database, properties):
                return None
            
            record = DatabaseRecord(
                record_id=str(uuid.uuid4()),
                database_id=database_id,
                properties=properties,
                created_by=user_id,
                last_edited_by=user_id
            )
            
            database.records.append(record)
            database.updated_at = datetime.now()
            
            # Queue for processing
            self.record_queue.put({
                'action': 'add',
                'record': record
            })
            
            logger.info(f"Record added: {record.record_id}")
            return record
            
        except Exception as e:
            logger.error(f"Error adding record: {str(e)}")
            return None
    
    def update_record(self, database_id: str, record_id: str, properties: Dict[str, Any], user_id: str) -> bool:
        """Update a record"""
        try:
            if database_id not in self.databases:
                return False
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return False
            
            # Find record
            record = None
            for r in database.records:
                if r.record_id == record_id:
                    record = r
                    break
            
            if not record:
                return False
            
            # Validate properties
            if not self._validate_record_properties(database, properties):
                return False
            
            # Update properties
            record.properties.update(properties)
            record.updated_at = datetime.now()
            record.last_edited_by = user_id
            
            database.updated_at = datetime.now()
            
            # Queue for processing
            self.record_queue.put({
                'action': 'update',
                'record': record
            })
            
            logger.info(f"Record updated: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating record: {str(e)}")
            return False
    
    def delete_record(self, database_id: str, record_id: str, user_id: str) -> bool:
        """Delete a record"""
        try:
            if database_id not in self.databases:
                return False
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_edit_database(database, user_id):
                return False
            
            # Find and archive record
            for record in database.records:
                if record.record_id == record_id:
                    record.is_archived = True
                    record.updated_at = datetime.now()
                    record.last_edited_by = user_id
                    
                    database.updated_at = datetime.now()
                    
                    # Queue for processing
                    self.record_queue.put({
                        'action': 'delete',
                        'record': record
                    })
                    
                    logger.info(f"Record deleted: {record_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            return False
    
    def query_records(self, database_id: str, view_id: str = None, filters: List[Dict[str, Any]] = None,
                     sorts: List[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[DatabaseRecord]:
        """Query records from a database"""
        try:
            if database_id not in self.databases:
                return []
            
            database = self.databases[database_id]
            records = [r for r in database.records if not r.is_archived]
            
            # Apply view filters if specified
            if view_id:
                view = self._get_view(database, view_id)
                if view:
                    records = self._apply_view_filters(records, view)
            
            # Apply custom filters
            if filters:
                records = self._apply_filters(records, filters)
            
            # Apply sorts
            if sorts:
                records = self._apply_sorts(records, sorts)
            elif view_id:
                view = self._get_view(database, view_id)
                if view and view.sorts:
                    records = self._apply_sorts(records, view.sorts)
            
            # Apply pagination
            records = records[offset:offset + limit]
            
            return records
            
        except Exception as e:
            logger.error(f"Error querying records: {str(e)}")
            return []
    
    def get_database(self, database_id: str, user_id: str) -> Optional[Database]:
        """Get a database by ID"""
        try:
            if database_id not in self.databases:
                return None
            
            database = self.databases[database_id]
            
            # Check permissions
            if not self._can_view_database(database, user_id):
                return None
            
            return database
            
        except Exception as e:
            logger.error(f"Error getting database: {str(e)}")
            return None
    
    def get_user_databases(self, user_id: str, workspace_id: str = None) -> List[Database]:
        """Get all databases for a user"""
        try:
            databases = []
            
            for database in self.databases.values():
                # Check workspace filter
                if workspace_id and database.workspace_id != workspace_id:
                    continue
                
                # Check permissions
                if self._can_view_database(database, user_id):
                    databases.append(database)
            
            # Sort by updated date (newest first)
            databases.sort(key=lambda x: x.updated_at, reverse=True)
            
            return databases
            
        except Exception as e:
            logger.error(f"Error getting user databases: {str(e)}")
            return []
    
    def search_databases(self, query: str, user_id: str, workspace_id: str = None) -> List[Database]:
        """Search databases by query"""
        try:
            query_lower = query.lower()
            results = []
            
            for database in self.databases.values():
                # Check workspace filter
                if workspace_id and database.workspace_id != workspace_id:
                    continue
                
                # Check permissions
                if not self._can_view_database(database, user_id):
                    continue
                
                # Search in title and description
                if (query_lower in database.title.lower() or
                    query_lower in database.description.lower()):
                    results.append(database)
            
            # Sort by relevance (title matches first)
            results.sort(key=lambda x: (
                query_lower not in x.title.lower(),
                x.updated_at
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching databases: {str(e)}")
            return []
    
    def _add_default_properties(self, database: Database):
        """Add default properties to a database"""
        try:
            for prop_type, prop_data in self.default_properties.items():
                property_obj = Property(
                    property_id=str(uuid.uuid4()),
                    name=prop_data['name'],
                    property_type=prop_type,
                    description=prop_data['description'],
                    is_required=prop_data.get('is_required', False),
                    is_unique=prop_data.get('is_unique', False)
                )
                
                database.properties[property_obj.property_id] = property_obj
            
        except Exception as e:
            logger.error(f"Error adding default properties: {str(e)}")
    
    def _add_property_to_database(self, database: Database, property_data: Dict[str, Any]):
        """Add a property to a database"""
        try:
            property_obj = Property(
                property_id=str(uuid.uuid4()),
                name=property_data['name'],
                property_type=PropertyType(property_data['type']),
                description=property_data.get('description', ''),
                options=property_data.get('options', []),
                formula=property_data.get('formula', ''),
                relation_database_id=property_data.get('relation_database_id', ''),
                relation_property_id=property_data.get('relation_property_id', ''),
                rollup_property=property_data.get('rollup_property', ''),
                rollup_function=property_data.get('rollup_function', ''),
                is_required=property_data.get('is_required', False),
                is_unique=property_data.get('is_unique', False),
                default_value=property_data.get('default_value')
            )
            
            database.properties[property_obj.property_id] = property_obj
            
        except Exception as e:
            logger.error(f"Error adding property to database: {str(e)}")
    
    def _create_default_view(self, database: Database):
        """Create default view for a database"""
        try:
            view = DatabaseView(
                view_id=str(uuid.uuid4()),
                name='Table',
                view_type=ViewType.TABLE,
                database_id=database.database_id,
                created_by=database.created_by,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                properties=list(database.properties.keys()),
                is_default=True
            )
            
            database.views.append(view)
            
        except Exception as e:
            logger.error(f"Error creating default view: {str(e)}")
    
    def _validate_record_properties(self, database: Database, properties: Dict[str, Any]) -> bool:
        """Validate record properties against database schema"""
        try:
            for property_id, value in properties.items():
                if property_id not in database.properties:
                    continue
                
                property_obj = database.properties[property_id]
                
                # Check required properties
                if property_obj.is_required and (value is None or value == ''):
                    return False
                
                # Validate property type
                if not self._validate_property_value(property_obj, value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating record properties: {str(e)}")
            return False
    
    def _validate_property_value(self, property_obj: Property, value: Any) -> bool:
        """Validate a property value"""
        try:
            if property_obj.property_type == PropertyType.TITLE:
                return isinstance(value, str)
            elif property_obj.property_type == PropertyType.TEXT:
                return isinstance(value, str)
            elif property_obj.property_type == PropertyType.NUMBER:
                return isinstance(value, (int, float))
            elif property_obj.property_type == PropertyType.SELECT:
                return value in property_obj.options
            elif property_obj.property_type == PropertyType.MULTI_SELECT:
                return isinstance(value, list) and all(v in property_obj.options for v in value)
            elif property_obj.property_type == PropertyType.DATE:
                return isinstance(value, (str, datetime))
            elif property_obj.property_type == PropertyType.CHECKBOX:
                return isinstance(value, bool)
            elif property_obj.property_type == PropertyType.URL:
                return isinstance(value, str) and value.startswith(('http://', 'https://'))
            elif property_obj.property_type == PropertyType.EMAIL:
                return isinstance(value, str) and '@' in value
            elif property_obj.property_type == PropertyType.PHONE:
                return isinstance(value, str)
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error validating property value: {str(e)}")
            return False
    
    def _get_view(self, database: Database, view_id: str) -> Optional[DatabaseView]:
        """Get a view by ID"""
        try:
            for view in database.views:
                if view.view_id == view_id:
                    return view
            return None
            
        except Exception as e:
            logger.error(f"Error getting view: {str(e)}")
            return None
    
    def _apply_view_filters(self, records: List[DatabaseRecord], view: DatabaseView) -> List[DatabaseRecord]:
        """Apply view filters to records"""
        try:
            if not view.filters:
                return records
            
            return self._apply_filters(records, view.filters)
            
        except Exception as e:
            logger.error(f"Error applying view filters: {str(e)}")
            return records
    
    def _apply_filters(self, records: List[DatabaseRecord], filters: List[Dict[str, Any]]) -> List[DatabaseRecord]:
        """Apply filters to records"""
        try:
            filtered_records = records
            
            for filter_data in filters:
                property_id = filter_data.get('property_id')
                filter_type = filter_data.get('type')
                value = filter_data.get('value')
                
                if not property_id or not filter_type:
                    continue
                
                filtered_records = [
                    record for record in filtered_records
                    if self._matches_filter(record, property_id, filter_type, value)
                ]
            
            return filtered_records
            
        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            return records
    
    def _matches_filter(self, record: DatabaseRecord, property_id: str, filter_type: str, value: Any) -> bool:
        """Check if a record matches a filter"""
        try:
            record_value = record.properties.get(property_id)
            
            if filter_type == FilterType.EQUALS.value:
                return record_value == value
            elif filter_type == FilterType.DOES_NOT_EQUAL.value:
                return record_value != value
            elif filter_type == FilterType.CONTAINS.value:
                return isinstance(record_value, str) and value in record_value
            elif filter_type == FilterType.DOES_NOT_CONTAIN.value:
                return not (isinstance(record_value, str) and value in record_value)
            elif filter_type == FilterType.STARTS_WITH.value:
                return isinstance(record_value, str) and record_value.startswith(value)
            elif filter_type == FilterType.ENDS_WITH.value:
                return isinstance(record_value, str) and record_value.endswith(value)
            elif filter_type == FilterType.IS_EMPTY.value:
                return record_value is None or record_value == ''
            elif filter_type == FilterType.IS_NOT_EMPTY.value:
                return record_value is not None and record_value != ''
            elif filter_type == FilterType.GREATER_THAN.value:
                return isinstance(record_value, (int, float)) and record_value > value
            elif filter_type == FilterType.LESS_THAN.value:
                return isinstance(record_value, (int, float)) and record_value < value
            elif filter_type == FilterType.GREATER_THAN_OR_EQUAL_TO.value:
                return isinstance(record_value, (int, float)) and record_value >= value
            elif filter_type == FilterType.LESS_THAN_OR_EQUAL_TO.value:
                return isinstance(record_value, (int, float)) and record_value <= value
            else:
                return True
                
        except Exception as e:
            logger.error(f"Error matching filter: {str(e)}")
            return True
    
    def _apply_sorts(self, records: List[DatabaseRecord], sorts: List[Dict[str, Any]]) -> List[DatabaseRecord]:
        """Apply sorts to records"""
        try:
            for sort_data in reversed(sorts):
                property_id = sort_data.get('property_id')
                direction = sort_data.get('direction', SortDirection.ASCENDING.value)
                
                if not property_id:
                    continue
                
                reverse = direction == SortDirection.DESCENDING.value
                
                records.sort(
                    key=lambda r: r.properties.get(property_id, ''),
                    reverse=reverse
                )
            
            return records
            
        except Exception as e:
            logger.error(f"Error applying sorts: {str(e)}")
            return records
    
    def _can_view_database(self, database: Database, user_id: str) -> bool:
        """Check if user can view database"""
        try:
            # Check if user has view permissions
            if user_id in database.permissions:
                return True
            
            # Check if database is public
            if database.is_public:
                return True
            
            # Check workspace permissions
            # This would check workspace membership
            return True  # Simplified for now
            
        except Exception as e:
            logger.error(f"Error checking database view permissions: {str(e)}")
            return False
    
    def _can_edit_database(self, database: Database, user_id: str) -> bool:
        """Check if user can edit database"""
        try:
            # Check if user has edit permissions
            if user_id in database.permissions:
                permission = database.permissions[user_id]
                return permission in ['edit', 'full_access']
            
            # Check if user is creator
            if user_id == database.created_by:
                return True
            
            # Check workspace admin permissions
            # This would check workspace admin status
            return False  # Simplified for now
            
        except Exception as e:
            logger.error(f"Error checking database edit permissions: {str(e)}")
            return False
    
    def _handle_record_processing(self, record_data: Dict[str, Any]):
        """Handle record processing"""
        try:
            action = record_data.get('action')
            record = record_data.get('record')
            
            if action == 'add':
                self._process_record_addition(record)
            elif action == 'update':
                self._process_record_update(record)
            elif action == 'delete':
                self._process_record_deletion(record)
            
        except Exception as e:
            logger.error(f"Error handling record processing: {str(e)}")
    
    def _process_record_addition(self, record: DatabaseRecord):
        """Process record addition"""
        try:
            # This would implement record addition processing
            # For now, we'll just log the action
            logger.info(f"Record addition processed: {record.record_id}")
            
        except Exception as e:
            logger.error(f"Error processing record addition: {str(e)}")
    
    def _process_record_update(self, record: DatabaseRecord):
        """Process record update"""
        try:
            # This would implement record update processing
            # For now, we'll just log the action
            logger.info(f"Record update processed: {record.record_id}")
            
        except Exception as e:
            logger.error(f"Error processing record update: {str(e)}")
    
    def _process_record_deletion(self, record: DatabaseRecord):
        """Process record deletion"""
        try:
            # This would implement record deletion processing
            # For now, we'll just log the action
            logger.info(f"Record deletion processed: {record.record_id}")
            
        except Exception as e:
            logger.error(f"Error processing record deletion: {str(e)}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get database system analytics"""
        try:
            return {
                'total_databases': len(self.databases),
                'total_records': sum(len(db.records) for db in self.databases.values()),
                'total_properties': sum(len(db.properties) for db in self.databases.values()),
                'total_views': sum(len(db.views) for db in self.databases.values()),
                'public_databases': len([db for db in self.databases.values() if db.is_public]),
                'databases_by_type': {
                    'table': len([db for db in self.databases.values() if db.settings.get('type') == 'table']),
                    'board': len([db for db in self.databases.values() if db.settings.get('type') == 'board']),
                    'timeline': len([db for db in self.databases.values() if db.settings.get('type') == 'timeline']),
                    'calendar': len([db for db in self.databases.values() if db.settings.get('type') == 'calendar']),
                    'gallery': len([db for db in self.databases.values() if db.settings.get('type') == 'gallery'])
                },
                'properties_by_type': {
                    prop_type.value: sum(
                        len([p for p in db.properties.values() if p.property_type == prop_type])
                        for db in self.databases.values()
                    )
                    for prop_type in PropertyType
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global database system instance
database_system = DatabaseSystem()
