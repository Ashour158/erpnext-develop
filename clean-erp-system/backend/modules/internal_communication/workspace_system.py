# Workspace System
# Notion-like workspace and page management system

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

class PageType(Enum):
    PAGE = "page"
    DATABASE = "database"
    TEMPLATE = "template"
    WIKI = "wiki"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"

class BlockType(Enum):
    TEXT = "text"
    HEADING = "heading"
    BULLET_LIST = "bullet_list"
    NUMBERED_LIST = "numbered_list"
    TOGGLE = "toggle"
    QUOTE = "quote"
    CODE = "code"
    DIVIDER = "divider"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    EMBED = "embed"
    TABLE = "table"
    COLUMN = "column"
    CALL_OUT = "call_out"
    BOOKMARK = "bookmark"
    LINK = "link"
    MENTION = "mention"
    EQUATION = "equation"
    DATABASE_VIEW = "database_view"

class PermissionLevel(Enum):
    READ = "read"
    COMMENT = "comment"
    EDIT = "edit"
    FULL_ACCESS = "full_access"

class WorkspaceType(Enum):
    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"
    PUBLIC = "public"

@dataclass
class Workspace:
    workspace_id: str
    name: str
    description: str
    workspace_type: WorkspaceType
    created_by: str
    created_at: datetime
    updated_at: datetime
    members: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    is_public: bool = False
    icon: Optional[str] = None
    cover_image: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class Page:
    page_id: str
    title: str
    content: List[Dict[str, Any]] = field(default_factory=list)
    page_type: PageType = PageType.PAGE
    workspace_id: str = ""
    parent_id: Optional[str] = None
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_edited_by: str = ""
    is_published: bool = False
    is_archived: bool = False
    permissions: Dict[str, PermissionLevel] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    icon: Optional[str] = None
    cover_image: Optional[str] = None

@dataclass
class Block:
    block_id: str
    page_id: str
    block_type: BlockType
    content: Dict[str, Any] = field(default_factory=dict)
    children: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    position: int = 0
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_deleted: bool = False

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
    properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    views: List[Dict[str, Any]] = field(default_factory=list)
    records: List[Dict[str, Any]] = field(default_factory=list)
    is_public: bool = False
    permissions: Dict[str, PermissionLevel] = field(default_factory=dict)

@dataclass
class Comment:
    comment_id: str
    page_id: str
    block_id: Optional[str] = None
    user_id: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_resolved: bool = False
    parent_id: Optional[str] = None
    mentions: List[str] = field(default_factory=list)

class WorkspaceSystem:
    """
    Workspace System
    Notion-like workspace and page management system
    """
    
    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.pages: Dict[str, Page] = {}
        self.blocks: Dict[str, Block] = {}
        self.databases: Dict[str, Database] = {}
        self.comments: Dict[str, Comment] = {}
        self.page_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_processing()
        
        # Initialize default workspace
        self._initialize_default_workspace()
    
    def _start_processing(self):
        """Start background processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_pages, daemon=True)
        thread.start()
        
        logger.info("Workspace system processing started")
    
    def _process_pages(self):
        """Process pages in background"""
        while self.is_processing:
            try:
                page_data = self.page_queue.get(timeout=1)
                self._handle_page_processing(page_data)
                self.page_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing page: {str(e)}")
    
    def _initialize_default_workspace(self):
        """Initialize default workspace"""
        try:
            default_workspace = Workspace(
                workspace_id="default",
                name="Personal Workspace",
                description="Your personal workspace",
                workspace_type=WorkspaceType.PERSONAL,
                created_by="system",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_public=False
            )
            
            self.workspaces["default"] = default_workspace
            
            logger.info("Default workspace initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default workspace: {str(e)}")
    
    def create_workspace(self, name: str, description: str, workspace_type: WorkspaceType,
                        created_by: str, is_public: bool = False) -> Workspace:
        """Create a new workspace"""
        try:
            workspace = Workspace(
                workspace_id=str(uuid.uuid4()),
                name=name,
                description=description,
                workspace_type=workspace_type,
                created_by=created_by,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                is_public=is_public,
                members=[created_by],
                admins=[created_by]
            )
            
            self.workspaces[workspace.workspace_id] = workspace
            
            logger.info(f"Workspace created: {workspace.workspace_id}")
            return workspace
            
        except Exception as e:
            logger.error(f"Error creating workspace: {str(e)}")
            raise
    
    def create_page(self, title: str, workspace_id: str, created_by: str,
                   page_type: PageType = PageType.PAGE, parent_id: str = None,
                   content: List[Dict[str, Any]] = None) -> Page:
        """Create a new page"""
        try:
            page = Page(
                page_id=str(uuid.uuid4()),
                title=title,
                content=content or [],
                page_type=page_type,
                workspace_id=workspace_id,
                parent_id=parent_id,
                created_by=created_by,
                last_edited_by=created_by
            )
            
            self.pages[page.page_id] = page
            
            # Queue for processing
            self.page_queue.put({
                'action': 'create',
                'page': page
            })
            
            logger.info(f"Page created: {page.page_id}")
            return page
            
        except Exception as e:
            logger.error(f"Error creating page: {str(e)}")
            raise
    
    def update_page(self, page_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update a page"""
        try:
            if page_id not in self.pages:
                return False
            
            page = self.pages[page_id]
            
            # Check permissions
            if not self._can_edit_page(page, user_id):
                return False
            
            # Update fields
            for field, value in updates.items():
                if hasattr(page, field):
                    setattr(page, field, value)
            
            page.updated_at = datetime.now()
            page.last_edited_by = user_id
            
            # Queue for processing
            self.page_queue.put({
                'action': 'update',
                'page': page
            })
            
            logger.info(f"Page updated: {page_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating page: {str(e)}")
            return False
    
    def delete_page(self, page_id: str, user_id: str) -> bool:
        """Delete a page"""
        try:
            if page_id not in self.pages:
                return False
            
            page = self.pages[page_id]
            
            # Check permissions
            if not self._can_edit_page(page, user_id):
                return False
            
            # Archive page instead of deleting
            page.is_archived = True
            page.updated_at = datetime.now()
            page.last_edited_by = user_id
            
            # Queue for processing
            self.page_queue.put({
                'action': 'delete',
                'page': page
            })
            
            logger.info(f"Page deleted: {page_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting page: {str(e)}")
            return False
    
    def add_block(self, page_id: str, block_type: BlockType, content: Dict[str, Any],
                  position: int = 0, parent_id: str = None, created_by: str = "") -> Block:
        """Add a block to a page"""
        try:
            if page_id not in self.pages:
                return None
            
            block = Block(
                block_id=str(uuid.uuid4()),
                page_id=page_id,
                block_type=block_type,
                content=content,
                parent_id=parent_id,
                position=position,
                created_by=created_by
            )
            
            self.blocks[block.block_id] = block
            
            # Add to page content
            page = self.pages[page_id]
            page.content.append({
                'block_id': block.block_id,
                'type': block.block_type.value,
                'content': block.content
            })
            
            # Update page
            page.updated_at = datetime.now()
            page.last_edited_by = created_by
            
            logger.info(f"Block added: {block.block_id}")
            return block
            
        except Exception as e:
            logger.error(f"Error adding block: {str(e)}")
            return None
    
    def update_block(self, block_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update a block"""
        try:
            if block_id not in self.blocks:
                return False
            
            block = self.blocks[block_id]
            
            # Check permissions
            if not self._can_edit_page(self.pages[block.page_id], user_id):
                return False
            
            # Update fields
            for field, value in updates.items():
                if hasattr(block, field):
                    setattr(block, field, value)
            
            block.updated_at = datetime.now()
            
            # Update page content
            page = self.pages[block.page_id]
            for i, content_block in enumerate(page.content):
                if content_block['block_id'] == block_id:
                    page.content[i] = {
                        'block_id': block.block_id,
                        'type': block.block_type.value,
                        'content': block.content
                    }
                    break
            
            page.updated_at = datetime.now()
            page.last_edited_by = user_id
            
            logger.info(f"Block updated: {block_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating block: {str(e)}")
            return False
    
    def delete_block(self, block_id: str, user_id: str) -> bool:
        """Delete a block"""
        try:
            if block_id not in self.blocks:
                return False
            
            block = self.blocks[block_id]
            
            # Check permissions
            if not self._can_edit_page(self.pages[block.page_id], user_id):
                return False
            
            # Mark as deleted
            block.is_deleted = True
            block.updated_at = datetime.now()
            
            # Remove from page content
            page = self.pages[block.page_id]
            page.content = [cb for cb in page.content if cb['block_id'] != block_id]
            
            page.updated_at = datetime.now()
            page.last_edited_by = user_id
            
            logger.info(f"Block deleted: {block_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting block: {str(e)}")
            return False
    
    def create_database(self, title: str, description: str, workspace_id: str,
                       page_id: str, created_by: str, properties: Dict[str, Dict[str, Any]] = None) -> Database:
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
                updated_at=datetime.now(),
                properties=properties or {},
                views=[{
                    'view_id': str(uuid.uuid4()),
                    'name': 'Table',
                    'type': 'table',
                    'properties': list(properties.keys()) if properties else []
                }]
            )
            
            self.databases[database.database_id] = database
            
            logger.info(f"Database created: {database.database_id}")
            return database
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            raise
    
    def add_database_record(self, database_id: str, properties: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Add a record to a database"""
        try:
            if database_id not in self.databases:
                return None
            
            database = self.databases[database_id]
            
            record = {
                'record_id': str(uuid.uuid4()),
                'properties': properties,
                'created_by': created_by,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            database.records.append(record)
            database.updated_at = datetime.now()
            
            logger.info(f"Database record added: {record['record_id']}")
            return record
            
        except Exception as e:
            logger.error(f"Error adding database record: {str(e)}")
            return None
    
    def update_database_record(self, database_id: str, record_id: str, properties: Dict[str, Any], user_id: str) -> bool:
        """Update a database record"""
        try:
            if database_id not in self.databases:
                return False
            
            database = self.databases[database_id]
            
            # Find record
            for record in database.records:
                if record['record_id'] == record_id:
                    record['properties'].update(properties)
                    record['updated_at'] = datetime.now().isoformat()
                    database.updated_at = datetime.now()
                    
                    logger.info(f"Database record updated: {record_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating database record: {str(e)}")
            return False
    
    def add_comment(self, page_id: str, user_id: str, content: str, block_id: str = None) -> Comment:
        """Add a comment to a page or block"""
        try:
            comment = Comment(
                comment_id=str(uuid.uuid4()),
                page_id=page_id,
                block_id=block_id,
                user_id=user_id,
                content=content
            )
            
            self.comments[comment.comment_id] = comment
            
            logger.info(f"Comment added: {comment.comment_id}")
            return comment
            
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            raise
    
    def get_page(self, page_id: str, user_id: str) -> Optional[Page]:
        """Get a page by ID"""
        try:
            if page_id not in self.pages:
                return None
            
            page = self.pages[page_id]
            
            # Check permissions
            if not self._can_view_page(page, user_id):
                return None
            
            return page
            
        except Exception as e:
            logger.error(f"Error getting page: {str(e)}")
            return None
    
    def get_workspace_pages(self, workspace_id: str, user_id: str) -> List[Page]:
        """Get all pages in a workspace"""
        try:
            pages = [
                page for page in self.pages.values()
                if page.workspace_id == workspace_id and not page.is_archived
            ]
            
            # Filter by permissions
            accessible_pages = [
                page for page in pages
                if self._can_view_page(page, user_id)
            ]
            
            # Sort by updated date (newest first)
            accessible_pages.sort(key=lambda x: x.updated_at, reverse=True)
            
            return accessible_pages
            
        except Exception as e:
            logger.error(f"Error getting workspace pages: {str(e)}")
            return []
    
    def search_pages(self, query: str, user_id: str, workspace_id: str = None) -> List[Page]:
        """Search pages by query"""
        try:
            query_lower = query.lower()
            results = []
            
            for page in self.pages.values():
                # Check workspace filter
                if workspace_id and page.workspace_id != workspace_id:
                    continue
                
                # Check permissions
                if not self._can_view_page(page, user_id):
                    continue
                
                # Skip archived pages
                if page.is_archived:
                    continue
                
                # Search in title and content
                if (query_lower in page.title.lower() or
                    any(query_lower in str(block.get('content', '')).lower() 
                        for block in page.content)):
                    results.append(page)
            
            # Sort by relevance (title matches first)
            results.sort(key=lambda x: (
                query_lower not in x.title.lower(),
                x.updated_at
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching pages: {str(e)}")
            return []
    
    def get_page_comments(self, page_id: str, user_id: str) -> List[Comment]:
        """Get comments for a page"""
        try:
            if page_id not in self.pages:
                return []
            
            page = self.pages[page_id]
            
            # Check permissions
            if not self._can_view_page(page, user_id):
                return []
            
            comments = [
                comment for comment in self.comments.values()
                if comment.page_id == page_id and not comment.is_resolved
            ]
            
            # Sort by created date (oldest first)
            comments.sort(key=lambda x: x.created_at)
            
            return comments
            
        except Exception as e:
            logger.error(f"Error getting page comments: {str(e)}")
            return []
    
    def _can_view_page(self, page: Page, user_id: str) -> bool:
        """Check if user can view page"""
        try:
            # Check if user is in permissions
            if user_id in page.permissions:
                return True
            
            # Check workspace permissions
            workspace = self.workspaces.get(page.workspace_id)
            if workspace and user_id in workspace.members:
                return True
            
            # Check if page is public
            if page.is_published:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking page view permissions: {str(e)}")
            return False
    
    def _can_edit_page(self, page: Page, user_id: str) -> bool:
        """Check if user can edit page"""
        try:
            # Check if user has edit permissions
            if user_id in page.permissions:
                permission = page.permissions[user_id]
                return permission in [PermissionLevel.EDIT, PermissionLevel.FULL_ACCESS]
            
            # Check workspace admin permissions
            workspace = self.workspaces.get(page.workspace_id)
            if workspace and user_id in workspace.admins:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking page edit permissions: {str(e)}")
            return False
    
    def _handle_page_processing(self, page_data: Dict[str, Any]):
        """Handle page processing"""
        try:
            action = page_data.get('action')
            page = page_data.get('page')
            
            if action == 'create':
                self._process_page_creation(page)
            elif action == 'update':
                self._process_page_update(page)
            elif action == 'delete':
                self._process_page_deletion(page)
            
        except Exception as e:
            logger.error(f"Error handling page processing: {str(e)}")
    
    def _process_page_creation(self, page: Page):
        """Process page creation"""
        try:
            # Create default blocks if needed
            if not page.content:
                self._create_default_blocks(page)
            
            # Index page for search
            self._index_page_for_search(page)
            
            logger.info(f"Page creation processed: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error processing page creation: {str(e)}")
    
    def _process_page_update(self, page: Page):
        """Process page update"""
        try:
            # Update search index
            self._index_page_for_search(page)
            
            # Process content changes
            self._process_content_changes(page)
            
            logger.info(f"Page update processed: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error processing page update: {str(e)}")
    
    def _process_page_deletion(self, page: Page):
        """Process page deletion"""
        try:
            # Remove from search index
            self._remove_page_from_search(page)
            
            # Archive related blocks
            self._archive_page_blocks(page)
            
            logger.info(f"Page deletion processed: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error processing page deletion: {str(e)}")
    
    def _create_default_blocks(self, page: Page):
        """Create default blocks for new page"""
        try:
            # Add title block
            title_block = {
                'block_id': str(uuid.uuid4()),
                'type': 'heading',
                'content': {'text': page.title, 'level': 1}
            }
            
            # Add empty text block
            text_block = {
                'block_id': str(uuid.uuid4()),
                'type': 'text',
                'content': {'text': ''}
            }
            
            page.content = [title_block, text_block]
            
        except Exception as e:
            logger.error(f"Error creating default blocks: {str(e)}")
    
    def _index_page_for_search(self, page: Page):
        """Index page for search"""
        try:
            # This would implement search indexing
            # For now, we'll just log the action
            logger.info(f"Page indexed for search: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error indexing page for search: {str(e)}")
    
    def _remove_page_from_search(self, page: Page):
        """Remove page from search index"""
        try:
            # This would implement search index removal
            # For now, we'll just log the action
            logger.info(f"Page removed from search index: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error removing page from search index: {str(e)}")
    
    def _process_content_changes(self, page: Page):
        """Process content changes"""
        try:
            # This would implement content change processing
            # For now, we'll just log the action
            logger.info(f"Content changes processed: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error processing content changes: {str(e)}")
    
    def _archive_page_blocks(self, page: Page):
        """Archive page blocks"""
        try:
            # This would implement block archiving
            # For now, we'll just log the action
            logger.info(f"Page blocks archived: {page.page_id}")
            
        except Exception as e:
            logger.error(f"Error archiving page blocks: {str(e)}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get workspace system analytics"""
        try:
            return {
                'total_workspaces': len(self.workspaces),
                'total_pages': len(self.pages),
                'total_blocks': len(self.blocks),
                'total_databases': len(self.databases),
                'total_comments': len(self.comments),
                'active_pages': len([p for p in self.pages.values() if not p.is_archived]),
                'published_pages': len([p for p in self.pages.values() if p.is_published]),
                'pages_by_type': {
                    page_type.value: len([p for p in self.pages.values() if p.page_type == page_type])
                    for page_type in PageType
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global workspace system instance
workspace_system = WorkspaceSystem()
