# Collaborative Editing System
# Real-time collaborative editing with operational transformation

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

class OperationType(Enum):
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    FORMAT = "format"
    ATTRIBUTE = "attribute"

class ConflictResolution(Enum):
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL = "manual"
    AUTOMATIC = "automatic"

@dataclass
class Operation:
    operation_id: str
    user_id: str
    page_id: str
    block_id: str
    operation_type: OperationType
    position: int
    length: int
    content: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 0
    is_applied: bool = False

@dataclass
class Cursor:
    user_id: str
    page_id: str
    block_id: str
    position: int
    selection_start: int = 0
    selection_end: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class EditSession:
    session_id: str
    page_id: str
    user_id: str
    started_at: datetime
    last_activity: datetime
    operations: List[Operation] = field(default_factory=list)
    cursors: List[Cursor] = field(default_factory=list)
    is_active: bool = True

@dataclass
class Conflict:
    conflict_id: str
    page_id: str
    block_id: str
    operation1: Operation
    operation2: Operation
    created_at: datetime
    resolution: ConflictResolution = ConflictResolution.AUTOMATIC
    is_resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

class CollaborativeEditingSystem:
    """
    Collaborative Editing System
    Real-time collaborative editing with operational transformation
    """
    
    def __init__(self):
        self.edit_sessions: Dict[str, EditSession] = {}
        self.operations: Dict[str, Operation] = {}
        self.cursors: Dict[str, Cursor] = {}
        self.conflicts: Dict[str, Conflict] = {}
        self.operation_queue = queue.Queue()
        self.is_processing = True
        
        # Start background processing
        self._start_processing()
        
        # Initialize operational transformation
        self._initialize_operational_transformation()
    
    def _start_processing(self):
        """Start background processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_operations, daemon=True)
        thread.start()
        
        logger.info("Collaborative editing system processing started")
    
    def _process_operations(self):
        """Process operations in background"""
        while self.is_processing:
            try:
                operation_data = self.operation_queue.get(timeout=1)
                self._handle_operation(operation_data)
                self.operation_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing operation: {str(e)}")
    
    def _initialize_operational_transformation(self):
        """Initialize operational transformation algorithms"""
        self.ot_algorithms = {
            'text': self._transform_text_operations,
            'rich_text': self._transform_rich_text_operations,
            'list': self._transform_list_operations,
            'table': self._transform_table_operations
        }
    
    def start_edit_session(self, page_id: str, user_id: str) -> EditSession:
        """Start a new edit session"""
        try:
            session = EditSession(
                session_id=str(uuid.uuid4()),
                page_id=page_id,
                user_id=user_id,
                started_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            self.edit_sessions[session.session_id] = session
            
            logger.info(f"Edit session started: {session.session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting edit session: {str(e)}")
            raise
    
    def end_edit_session(self, session_id: str, user_id: str) -> bool:
        """End an edit session"""
        try:
            if session_id not in self.edit_sessions:
                return False
            
            session = self.edit_sessions[session_id]
            
            # Check permissions
            if session.user_id != user_id:
                return False
            
            session.is_active = False
            
            # Remove user cursors
            self._remove_user_cursors(user_id, session.page_id)
            
            logger.info(f"Edit session ended: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending edit session: {str(e)}")
            return False
    
    def apply_operation(self, page_id: str, block_id: str, user_id: str,
                       operation_type: OperationType, position: int, length: int,
                       content: str = "", attributes: Dict[str, Any] = None) -> Operation:
        """Apply an operation"""
        try:
            operation = Operation(
                operation_id=str(uuid.uuid4()),
                user_id=user_id,
                page_id=page_id,
                block_id=block_id,
                operation_type=operation_type,
                position=position,
                length=length,
                content=content,
                attributes=attributes or {}
            )
            
            # Transform operation against concurrent operations
            transformed_operation = self._transform_operation(operation)
            
            # Apply the transformed operation
            self._apply_transformed_operation(transformed_operation)
            
            # Store operation
            self.operations[operation.operation_id] = operation
            
            # Queue for processing
            self.operation_queue.put({
                'action': 'apply',
                'operation': operation
            })
            
            logger.info(f"Operation applied: {operation.operation_id}")
            return operation
            
        except Exception as e:
            logger.error(f"Error applying operation: {str(e)}")
            raise
    
    def update_cursor(self, page_id: str, block_id: str, user_id: str,
                     position: int, selection_start: int = 0, selection_end: int = 0) -> Cursor:
        """Update user cursor position"""
        try:
            cursor_id = f"{user_id}_{page_id}_{block_id}"
            
            cursor = Cursor(
                user_id=user_id,
                page_id=page_id,
                block_id=block_id,
                position=position,
                selection_start=selection_start,
                selection_end=selection_end
            )
            
            self.cursors[cursor_id] = cursor
            
            # Broadcast cursor update
            self._broadcast_cursor_update(cursor)
            
            logger.info(f"Cursor updated: {cursor_id}")
            return cursor
            
        except Exception as e:
            logger.error(f"Error updating cursor: {str(e)}")
            raise
    
    def get_cursors(self, page_id: str, user_id: str) -> List[Cursor]:
        """Get all cursors for a page"""
        try:
            cursors = [
                cursor for cursor in self.cursors.values()
                if cursor.page_id == page_id and cursor.user_id != user_id and cursor.is_active
            ]
            
            # Filter out old cursors
            now = datetime.now()
            active_cursors = [
                cursor for cursor in cursors
                if (now - cursor.timestamp).seconds < 30
            ]
            
            return active_cursors
            
        except Exception as e:
            logger.error(f"Error getting cursors: {str(e)}")
            return []
    
    def get_operations(self, page_id: str, block_id: str, since: datetime = None) -> List[Operation]:
        """Get operations for a page/block since a timestamp"""
        try:
            operations = [
                op for op in self.operations.values()
                if op.page_id == page_id and op.block_id == block_id
            ]
            
            if since:
                operations = [
                    op for op in operations
                    if op.timestamp > since
                ]
            
            # Sort by timestamp
            operations.sort(key=lambda x: x.timestamp)
            
            return operations
            
        except Exception as e:
            logger.error(f"Error getting operations: {str(e)}")
            return []
    
    def resolve_conflict(self, conflict_id: str, user_id: str, resolution: str) -> bool:
        """Resolve a conflict"""
        try:
            if conflict_id not in self.conflicts:
                return False
            
            conflict = self.conflicts[conflict_id]
            
            # Check permissions
            if not self._can_resolve_conflict(conflict, user_id):
                return False
            
            # Apply resolution
            if resolution == "operation1":
                self._apply_operation(conflict.operation1)
            elif resolution == "operation2":
                self._apply_operation(conflict.operation2)
            elif resolution == "merge":
                self._merge_operations(conflict.operation1, conflict.operation2)
            
            # Mark as resolved
            conflict.is_resolved = True
            conflict.resolved_by = user_id
            conflict.resolved_at = datetime.now()
            
            logger.info(f"Conflict resolved: {conflict_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving conflict: {str(e)}")
            return False
    
    def _transform_operation(self, operation: Operation) -> Operation:
        """Transform operation against concurrent operations"""
        try:
            # Get concurrent operations
            concurrent_ops = self._get_concurrent_operations(operation)
            
            # Apply operational transformation
            transformed_operation = operation
            for concurrent_op in concurrent_ops:
                transformed_operation = self._transform_against_operation(
                    transformed_operation, concurrent_op
                )
            
            return transformed_operation
            
        except Exception as e:
            logger.error(f"Error transforming operation: {str(e)}")
            return operation
    
    def _get_concurrent_operations(self, operation: Operation) -> List[Operation]:
        """Get concurrent operations"""
        try:
            concurrent_ops = []
            
            for op in self.operations.values():
                if (op.page_id == operation.page_id and 
                    op.block_id == operation.block_id and
                    op.user_id != operation.user_id and
                    op.timestamp < operation.timestamp and
                    not op.is_applied):
                    concurrent_ops.append(op)
            
            return concurrent_ops
            
        except Exception as e:
            logger.error(f"Error getting concurrent operations: {str(e)}")
            return []
    
    def _transform_against_operation(self, op1: Operation, op2: Operation) -> Operation:
        """Transform operation against another operation"""
        try:
            # Determine transformation algorithm based on content type
            content_type = self._get_content_type(op1.page_id, op1.block_id)
            transform_func = self.ot_algorithms.get(content_type, self._transform_text_operations)
            
            return transform_func(op1, op2)
            
        except Exception as e:
            logger.error(f"Error transforming against operation: {str(e)}")
            return op1
    
    def _transform_text_operations(self, op1: Operation, op2: Operation) -> Operation:
        """Transform text operations"""
        try:
            if op1.operation_type == OperationType.INSERT and op2.operation_type == OperationType.INSERT:
                # Both insertions
                if op1.position <= op2.position:
                    return op1
                else:
                    # Adjust position
                    new_op = Operation(
                        operation_id=op1.operation_id,
                        user_id=op1.user_id,
                        page_id=op1.page_id,
                        block_id=op1.block_id,
                        operation_type=op1.operation_type,
                        position=op1.position + len(op2.content),
                        length=op1.length,
                        content=op1.content,
                        attributes=op1.attributes,
                        timestamp=op1.timestamp,
                        version=op1.version + 1
                    )
                    return new_op
            
            elif op1.operation_type == OperationType.INSERT and op2.operation_type == OperationType.DELETE:
                # Insert vs Delete
                if op1.position <= op2.position:
                    return op1
                else:
                    # Adjust position
                    new_op = Operation(
                        operation_id=op1.operation_id,
                        user_id=op1.user_id,
                        page_id=op1.page_id,
                        block_id=op1.block_id,
                        operation_type=op1.operation_type,
                        position=op1.position - op2.length,
                        length=op1.length,
                        content=op1.content,
                        attributes=op1.attributes,
                        timestamp=op1.timestamp,
                        version=op1.version + 1
                    )
                    return new_op
            
            elif op1.operation_type == OperationType.DELETE and op2.operation_type == OperationType.INSERT:
                # Delete vs Insert
                if op1.position < op2.position:
                    return op1
                else:
                    # Adjust position
                    new_op = Operation(
                        operation_id=op1.operation_id,
                        user_id=op1.user_id,
                        page_id=op1.page_id,
                        block_id=op1.block_id,
                        operation_type=op1.operation_type,
                        position=op1.position + len(op2.content),
                        length=op1.length,
                        content=op1.content,
                        attributes=op1.attributes,
                        timestamp=op1.timestamp,
                        version=op1.version + 1
                    )
                    return new_op
            
            elif op1.operation_type == OperationType.DELETE and op2.operation_type == OperationType.DELETE:
                # Both deletions
                if op1.position < op2.position:
                    return op1
                elif op1.position > op2.position:
                    # Adjust position
                    new_op = Operation(
                        operation_id=op1.operation_id,
                        user_id=op1.user_id,
                        page_id=op1.page_id,
                        block_id=op1.block_id,
                        operation_type=op1.operation_type,
                        position=op1.position - op2.length,
                        length=op1.length,
                        content=op1.content,
                        attributes=op1.attributes,
                        timestamp=op1.timestamp,
                        version=op1.version + 1
                    )
                    return new_op
                else:
                    # Same position - conflict
                    self._create_conflict(op1, op2)
                    return op1
            
            return op1
            
        except Exception as e:
            logger.error(f"Error transforming text operations: {str(e)}")
            return op1
    
    def _transform_rich_text_operations(self, op1: Operation, op2: Operation) -> Operation:
        """Transform rich text operations"""
        try:
            # Rich text operations are more complex due to formatting
            # This would implement rich text operational transformation
            return self._transform_text_operations(op1, op2)
            
        except Exception as e:
            logger.error(f"Error transforming rich text operations: {str(e)}")
            return op1
    
    def _transform_list_operations(self, op1: Operation, op2: Operation) -> Operation:
        """Transform list operations"""
        try:
            # List operations need special handling for item ordering
            # This would implement list operational transformation
            return self._transform_text_operations(op1, op2)
            
        except Exception as e:
            logger.error(f"Error transforming list operations: {str(e)}")
            return op1
    
    def _transform_table_operations(self, op1: Operation, op2: Operation) -> Operation:
        """Transform table operations"""
        try:
            # Table operations need special handling for cell positioning
            # This would implement table operational transformation
            return self._transform_text_operations(op1, op2)
            
        except Exception as e:
            logger.error(f"Error transforming table operations: {str(e)}")
            return op1
    
    def _get_content_type(self, page_id: str, block_id: str) -> str:
        """Get content type for a block"""
        try:
            # This would determine content type based on block metadata
            # For now, return default text type
            return 'text'
            
        except Exception as e:
            logger.error(f"Error getting content type: {str(e)}")
            return 'text'
    
    def _apply_transformed_operation(self, operation: Operation):
        """Apply a transformed operation"""
        try:
            # Mark as applied
            operation.is_applied = True
            
            # Broadcast operation to other users
            self._broadcast_operation(operation)
            
            logger.info(f"Transformed operation applied: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error applying transformed operation: {str(e)}")
    
    def _apply_operation(self, operation: Operation):
        """Apply an operation to content"""
        try:
            # This would apply the operation to the actual content
            # For now, we'll just log the action
            logger.info(f"Operation applied to content: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error applying operation: {str(e)}")
    
    def _merge_operations(self, op1: Operation, op2: Operation):
        """Merge two operations"""
        try:
            # This would implement operation merging
            # For now, we'll just log the action
            logger.info(f"Operations merged: {op1.operation_id} and {op2.operation_id}")
            
        except Exception as e:
            logger.error(f"Error merging operations: {str(e)}")
    
    def _create_conflict(self, op1: Operation, op2: Operation):
        """Create a conflict between operations"""
        try:
            conflict = Conflict(
                conflict_id=str(uuid.uuid4()),
                page_id=op1.page_id,
                block_id=op1.block_id,
                operation1=op1,
                operation2=op2,
                created_at=datetime.now()
            )
            
            self.conflicts[conflict.conflict_id] = conflict
            
            # Notify users about conflict
            self._notify_conflict(conflict)
            
            logger.info(f"Conflict created: {conflict.conflict_id}")
            
        except Exception as e:
            logger.error(f"Error creating conflict: {str(e)}")
    
    def _can_resolve_conflict(self, conflict: Conflict, user_id: str) -> bool:
        """Check if user can resolve conflict"""
        try:
            # Check if user is involved in the conflict
            return (user_id == conflict.operation1.user_id or 
                    user_id == conflict.operation2.user_id)
            
        except Exception as e:
            logger.error(f"Error checking conflict resolution permissions: {str(e)}")
            return False
    
    def _remove_user_cursors(self, user_id: str, page_id: str):
        """Remove user cursors from a page"""
        try:
            cursors_to_remove = [
                cursor_id for cursor_id, cursor in self.cursors.items()
                if cursor.user_id == user_id and cursor.page_id == page_id
            ]
            
            for cursor_id in cursors_to_remove:
                del self.cursors[cursor_id]
            
        except Exception as e:
            logger.error(f"Error removing user cursors: {str(e)}")
    
    def _broadcast_operation(self, operation: Operation):
        """Broadcast operation to other users"""
        try:
            # This would broadcast to WebSocket connections
            # For now, we'll just log the action
            logger.info(f"Operation broadcasted: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting operation: {str(e)}")
    
    def _broadcast_cursor_update(self, cursor: Cursor):
        """Broadcast cursor update to other users"""
        try:
            # This would broadcast to WebSocket connections
            # For now, we'll just log the action
            logger.info(f"Cursor update broadcasted: {cursor.user_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting cursor update: {str(e)}")
    
    def _notify_conflict(self, conflict: Conflict):
        """Notify users about conflict"""
        try:
            # This would send notifications to involved users
            # For now, we'll just log the action
            logger.info(f"Conflict notification sent: {conflict.conflict_id}")
            
        except Exception as e:
            logger.error(f"Error notifying conflict: {str(e)}")
    
    def _handle_operation(self, operation_data: Dict[str, Any]):
        """Handle operation processing"""
        try:
            action = operation_data.get('action')
            operation = operation_data.get('operation')
            
            if action == 'apply':
                self._process_operation_application(operation)
            elif action == 'transform':
                self._process_operation_transformation(operation)
            elif action == 'conflict':
                self._process_conflict_resolution(operation)
            
        except Exception as e:
            logger.error(f"Error handling operation: {str(e)}")
    
    def _process_operation_application(self, operation: Operation):
        """Process operation application"""
        try:
            # This would implement operation application processing
            # For now, we'll just log the action
            logger.info(f"Operation application processed: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error processing operation application: {str(e)}")
    
    def _process_operation_transformation(self, operation: Operation):
        """Process operation transformation"""
        try:
            # This would implement operation transformation processing
            # For now, we'll just log the action
            logger.info(f"Operation transformation processed: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error processing operation transformation: {str(e)}")
    
    def _process_conflict_resolution(self, operation: Operation):
        """Process conflict resolution"""
        try:
            # This would implement conflict resolution processing
            # For now, we'll just log the action
            logger.info(f"Conflict resolution processed: {operation.operation_id}")
            
        except Exception as e:
            logger.error(f"Error processing conflict resolution: {str(e)}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get collaborative editing analytics"""
        try:
            return {
                'active_sessions': len([s for s in self.edit_sessions.values() if s.is_active]),
                'total_operations': len(self.operations),
                'active_cursors': len([c for c in self.cursors.values() if c.is_active]),
                'total_conflicts': len(self.conflicts),
                'unresolved_conflicts': len([c for c in self.conflicts.values() if not c.is_resolved]),
                'operations_by_type': {
                    op_type.value: len([op for op in self.operations.values() if op.operation_type == op_type])
                    for op_type in OperationType
                },
                'average_session_duration': 0.0,  # Would calculate from actual data
                'conflict_resolution_rate': 0.0  # Would calculate from actual data
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global collaborative editing system instance
collaborative_editing_system = CollaborativeEditingSystem()
