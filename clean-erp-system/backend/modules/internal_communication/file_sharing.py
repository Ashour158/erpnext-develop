# File Sharing System
# Internal file sharing system with support for all file types

import os
import json
import logging
import uuid
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
import time
from pathlib import Path
import shutil
import base64
import hmac
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileType(Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    PDF = "pdf"
    OTHER = "other"

class FileStatus(Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"

class ShareType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    TEMPORARY = "temporary"

@dataclass
class SharedFile:
    file_id: str
    filename: str
    original_filename: str
    file_type: FileType
    mime_type: str
    size: int
    hash: str
    uploader_id: str
    upload_date: datetime
    status: FileStatus = FileStatus.UPLOADING
    share_type: ShareType = ShareType.PRIVATE
    permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    description: str = ""
    download_count: int = 0
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    file_path: str = ""
    thumbnail_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_encrypted: bool = False
    encryption_key: Optional[str] = None

@dataclass
class FileShare:
    share_id: str
    file_id: str
    shared_by: str
    shared_with: List[str]
    share_type: ShareType
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    is_active: bool = True

@dataclass
class FileComment:
    comment_id: str
    file_id: str
    user_id: str
    content: str
    created_at: datetime
    edited_at: Optional[datetime] = None
    is_edited: bool = False

class FileSharingSystem:
    """
    File Sharing System
    Handles file uploads, sharing, permissions, and management
    """
    
    def __init__(self):
        self.files: Dict[str, SharedFile] = {}
        self.shares: Dict[str, FileShare] = {}
        self.comments: Dict[str, List[FileComment]] = {}
        self.file_queue = queue.Queue()
        self.is_processing = True
        
        # File storage
        self.upload_dir = Path("uploads/files")
        self.thumbnails_dir = Path("uploads/thumbnails")
        self.temp_dir = Path("uploads/temp")
        
        # Create directories
        self._create_directories()
        
        # Start background processing
        self._start_file_processing()
        
        # Initialize file type mappings
        self._initialize_file_types()
    
    def _create_directories(self):
        """Create necessary directories"""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("File sharing directories created")
            
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
    
    def _start_file_processing(self):
        """Start background file processing"""
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self._process_files, daemon=True)
        thread.start()
        
        logger.info("File sharing system processing started")
    
    def _process_files(self):
        """Process files in background"""
        while self.is_processing:
            try:
                file_data = self.file_queue.get(timeout=1)
                self._handle_file_processing(file_data)
                self.file_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
    
    def _initialize_file_types(self):
        """Initialize file type mappings"""
        self.file_type_mappings = {
            # Documents
            '.pdf': FileType.PDF,
            '.doc': FileType.DOCUMENT,
            '.docx': FileType.DOCUMENT,
            '.txt': FileType.DOCUMENT,
            '.rtf': FileType.DOCUMENT,
            '.odt': FileType.DOCUMENT,
            
            # Images
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.bmp': FileType.IMAGE,
            '.svg': FileType.IMAGE,
            '.webp': FileType.IMAGE,
            '.tiff': FileType.IMAGE,
            
            # Videos
            '.mp4': FileType.VIDEO,
            '.avi': FileType.VIDEO,
            '.mov': FileType.VIDEO,
            '.wmv': FileType.VIDEO,
            '.flv': FileType.VIDEO,
            '.webm': FileType.VIDEO,
            '.mkv': FileType.VIDEO,
            
            # Audio
            '.mp3': FileType.AUDIO,
            '.wav': FileType.AUDIO,
            '.flac': FileType.AUDIO,
            '.aac': FileType.AUDIO,
            '.ogg': FileType.AUDIO,
            '.wma': FileType.AUDIO,
            
            # Archives
            '.zip': FileType.ARCHIVE,
            '.rar': FileType.ARCHIVE,
            '.7z': FileType.ARCHIVE,
            '.tar': FileType.ARCHIVE,
            '.gz': FileType.ARCHIVE,
            
            # Code
            '.py': FileType.CODE,
            '.js': FileType.CODE,
            '.html': FileType.CODE,
            '.css': FileType.CODE,
            '.java': FileType.CODE,
            '.cpp': FileType.CODE,
            '.c': FileType.CODE,
            '.php': FileType.CODE,
            '.rb': FileType.CODE,
            '.go': FileType.CODE,
            
            # Spreadsheets
            '.xls': FileType.SPREADSHEET,
            '.xlsx': FileType.SPREADSHEET,
            '.csv': FileType.SPREADSHEET,
            '.ods': FileType.SPREADSHEET,
            
            # Presentations
            '.ppt': FileType.PRESENTATION,
            '.pptx': FileType.PRESENTATION,
            '.odp': FileType.PRESENTATION
        }
    
    def upload_file(self, filename: str, file_data: bytes, uploader_id: str, 
                   description: str = "", tags: List[str] = None, 
                   share_type: ShareType = ShareType.PRIVATE) -> Optional[SharedFile]:
        """Upload a new file"""
        try:
            # Generate file ID and hash
            file_id = str(uuid.uuid4())
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Get file info
            file_size = len(file_data)
            file_extension = Path(filename).suffix.lower()
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            file_type = self.file_type_mappings.get(file_extension, FileType.OTHER)
            
            # Create file path
            file_path = self.upload_dir / f"{file_id}_{filename}"
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Create file record
            shared_file = SharedFile(
                file_id=file_id,
                filename=filename,
                original_filename=filename,
                file_type=file_type,
                mime_type=mime_type,
                size=file_size,
                hash=file_hash,
                uploader_id=uploader_id,
                upload_date=datetime.now(),
                status=FileStatus.UPLOADING,
                share_type=share_type,
                tags=tags or [],
                description=description,
                file_path=str(file_path)
            )
            
            # Store file record
            self.files[file_id] = shared_file
            
            # Queue for processing
            self.file_queue.put({
                'action': 'process',
                'file_id': file_id,
                'file_path': str(file_path)
            })
            
            logger.info(f"File uploaded: {filename} ({file_id})")
            return shared_file
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    def share_file(self, file_id: str, shared_by: str, shared_with: List[str], 
                  share_type: ShareType = ShareType.PRIVATE, 
                  permissions: List[str] = None, expires_at: datetime = None) -> Optional[FileShare]:
        """Share a file with other users"""
        try:
            if file_id not in self.files:
                return None
            
            # Create share record
            share_id = str(uuid.uuid4())
            file_share = FileShare(
                share_id=share_id,
                file_id=file_id,
                shared_by=shared_by,
                shared_with=shared_with,
                share_type=share_type,
                permissions=permissions or ['read'],
                created_at=datetime.now(),
                expires_at=expires_at
            )
            
            # Store share record
            self.shares[share_id] = file_share
            
            # Update file permissions
            self.files[file_id].permissions.extend(shared_with)
            
            logger.info(f"File shared: {file_id} with {len(shared_with)} users")
            return file_share
            
        except Exception as e:
            logger.error(f"Error sharing file: {str(e)}")
            return None
    
    def download_file(self, file_id: str, user_id: str) -> Optional[bytes]:
        """Download a file"""
        try:
            if file_id not in self.files:
                return None
            
            file = self.files[file_id]
            
            # Check permissions
            if not self._can_access_file(file_id, user_id):
                return None
            
            # Read file data
            with open(file.file_path, 'rb') as f:
                file_data = f.read()
            
            # Update access stats
            file.download_count += 1
            file.last_accessed = datetime.now()
            
            logger.info(f"File downloaded: {file_id} by {user_id}")
            return file_data
            
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return None
    
    def get_file_info(self, file_id: str, user_id: str) -> Optional[SharedFile]:
        """Get file information"""
        try:
            if file_id not in self.files:
                return None
            
            file = self.files[file_id]
            
            # Check permissions
            if not self._can_access_file(file_id, user_id):
                return None
            
            return file
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None
    
    def get_user_files(self, user_id: str, file_type: FileType = None) -> List[SharedFile]:
        """Get files for a user"""
        try:
            user_files = []
            
            for file in self.files.values():
                # Check if user can access file
                if self._can_access_file(file.file_id, user_id):
                    if file_type is None or file.file_type == file_type:
                        user_files.append(file)
            
            # Sort by upload date (newest first)
            user_files.sort(key=lambda x: x.upload_date, reverse=True)
            
            return user_files
            
        except Exception as e:
            logger.error(f"Error getting user files: {str(e)}")
            return []
    
    def search_files(self, user_id: str, query: str, file_type: FileType = None) -> List[SharedFile]:
        """Search files"""
        try:
            results = []
            query_lower = query.lower()
            
            for file in self.files.values():
                if self._can_access_file(file.file_id, user_id):
                    # Search in filename, description, and tags
                    if (query_lower in file.filename.lower() or 
                        query_lower in file.description.lower() or
                        any(query_lower in tag.lower() for tag in file.tags)):
                        
                        if file_type is None or file.file_type == file_type:
                            results.append(file)
            
            # Sort by relevance (filename matches first)
            results.sort(key=lambda x: (
                query_lower not in x.filename.lower(),
                x.upload_date
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching files: {str(e)}")
            return []
    
    def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file"""
        try:
            if file_id not in self.files:
                return False
            
            file = self.files[file_id]
            
            # Check permissions (only uploader or admin can delete)
            if file.uploader_id != user_id and not self._is_admin(user_id):
                return False
            
            # Delete physical file
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
            
            # Delete thumbnail if exists
            if file.thumbnail_path and os.path.exists(file.thumbnail_path):
                os.remove(file.thumbnail_path)
            
            # Update file status
            file.status = FileStatus.DELETED
            
            # Remove from active files
            del self.files[file_id]
            
            # Remove related shares
            shares_to_remove = [share_id for share_id, share in self.shares.items() if share.file_id == file_id]
            for share_id in shares_to_remove:
                del self.shares[share_id]
            
            logger.info(f"File deleted: {file_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def add_file_comment(self, file_id: str, user_id: str, content: str) -> Optional[FileComment]:
        """Add a comment to a file"""
        try:
            if file_id not in self.files:
                return None
            
            # Check permissions
            if not self._can_access_file(file_id, user_id):
                return None
            
            # Create comment
            comment_id = str(uuid.uuid4())
            comment = FileComment(
                comment_id=comment_id,
                file_id=file_id,
                user_id=user_id,
                content=content,
                created_at=datetime.now()
            )
            
            # Store comment
            if file_id not in self.comments:
                self.comments[file_id] = []
            self.comments[file_id].append(comment)
            
            logger.info(f"Comment added to file: {file_id} by {user_id}")
            return comment
            
        except Exception as e:
            logger.error(f"Error adding file comment: {str(e)}")
            return None
    
    def get_file_comments(self, file_id: str, user_id: str) -> List[FileComment]:
        """Get comments for a file"""
        try:
            if file_id not in self.files:
                return []
            
            # Check permissions
            if not self._can_access_file(file_id, user_id):
                return []
            
            return self.comments.get(file_id, [])
            
        except Exception as e:
            logger.error(f"Error getting file comments: {str(e)}")
            return []
    
    def edit_file_comment(self, comment_id: str, user_id: str, new_content: str) -> bool:
        """Edit a file comment"""
        try:
            # Find comment
            comment = self._find_comment(comment_id)
            if not comment:
                return False
            
            # Check permissions
            if comment.user_id != user_id:
                return False
            
            # Update comment
            comment.content = new_content
            comment.edited_at = datetime.now()
            comment.is_edited = True
            
            logger.info(f"Comment edited: {comment_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error editing file comment: {str(e)}")
            return False
    
    def delete_file_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete a file comment"""
        try:
            # Find comment
            comment = self._find_comment(comment_id)
            if not comment:
                return False
            
            # Check permissions
            if comment.user_id != user_id and not self._is_admin(user_id):
                return False
            
            # Remove comment
            if comment.file_id in self.comments:
                self.comments[comment.file_id] = [c for c in self.comments[comment.file_id] if c.comment_id != comment_id]
            
            logger.info(f"Comment deleted: {comment_id} by {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file comment: {str(e)}")
            return False
    
    def get_file_thumbnail(self, file_id: str, user_id: str) -> Optional[bytes]:
        """Get file thumbnail"""
        try:
            if file_id not in self.files:
                return None
            
            file = self.files[file_id]
            
            # Check permissions
            if not self._can_access_file(file_id, user_id):
                return None
            
            # Check if thumbnail exists
            if not file.thumbnail_path or not os.path.exists(file.thumbnail_path):
                return None
            
            # Read thumbnail
            with open(file.thumbnail_path, 'rb') as f:
                thumbnail_data = f.read()
            
            return thumbnail_data
            
        except Exception as e:
            logger.error(f"Error getting file thumbnail: {str(e)}")
            return None
    
    def _can_access_file(self, file_id: str, user_id: str) -> bool:
        """Check if user can access file"""
        try:
            if file_id not in self.files:
                return False
            
            file = self.files[file_id]
            
            # Check if user is uploader
            if file.uploader_id == user_id:
                return True
            
            # Check if user is in permissions
            if user_id in file.permissions:
                return True
            
            # Check if file is public
            if file.share_type == ShareType.PUBLIC:
                return True
            
            # Check if user is in any share
            for share in self.shares.values():
                if share.file_id == file_id and user_id in share.shared_with:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking file access: {str(e)}")
            return False
    
    def _is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        # This would check user permissions
        return False
    
    def _find_comment(self, comment_id: str) -> Optional[FileComment]:
        """Find comment by ID"""
        for comments in self.comments.values():
            for comment in comments:
                if comment.comment_id == comment_id:
                    return comment
        return None
    
    def _handle_file_processing(self, file_data: Dict[str, Any]):
        """Handle file processing"""
        try:
            action = file_data.get('action')
            file_id = file_data.get('file_id')
            
            if action == 'process':
                self._process_file(file_id, file_data.get('file_path'))
            elif action == 'generate_thumbnail':
                self._generate_thumbnail(file_id, file_data.get('file_path'))
            elif action == 'scan_virus':
                self._scan_virus(file_id, file_data.get('file_path'))
            
        except Exception as e:
            logger.error(f"Error handling file processing: {str(e)}")
    
    def _process_file(self, file_id: str, file_path: str):
        """Process uploaded file"""
        try:
            if file_id not in self.files:
                return
            
            file = self.files[file_id]
            
            # Update status
            file.status = FileStatus.PROCESSING
            
            # Generate thumbnail for images/videos
            if file.file_type in [FileType.IMAGE, FileType.VIDEO]:
                self._generate_thumbnail(file_id, file_path)
            
            # Scan for viruses
            self._scan_virus(file_id, file_path)
            
            # Extract metadata
            self._extract_metadata(file_id, file_path)
            
            # Update status
            file.status = FileStatus.READY
            
            logger.info(f"File processed: {file_id}")
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            if file_id in self.files:
                self.files[file_id].status = FileStatus.ERROR
    
    def _generate_thumbnail(self, file_id: str, file_path: str):
        """Generate thumbnail for file"""
        try:
            if file_id not in self.files:
                return
            
            file = self.files[file_id]
            
            # Create thumbnail path
            thumbnail_path = self.thumbnails_dir / f"{file_id}_thumb.jpg"
            
            # Generate thumbnail based on file type
            if file.file_type == FileType.IMAGE:
                self._generate_image_thumbnail(file_path, str(thumbnail_path))
            elif file.file_type == FileType.VIDEO:
                self._generate_video_thumbnail(file_path, str(thumbnail_path))
            elif file.file_type == FileType.PDF:
                self._generate_pdf_thumbnail(file_path, str(thumbnail_path))
            
            # Update file record
            file.thumbnail_path = str(thumbnail_path)
            
            logger.info(f"Thumbnail generated: {file_id}")
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
    
    def _generate_image_thumbnail(self, file_path: str, thumbnail_path: str):
        """Generate thumbnail for image"""
        try:
            # This would use PIL or similar library to generate thumbnail
            # For now, we'll create a placeholder
            with open(thumbnail_path, 'w') as f:
                f.write(f"Thumbnail for {file_path}")
            
        except Exception as e:
            logger.error(f"Error generating image thumbnail: {str(e)}")
    
    def _generate_video_thumbnail(self, file_path: str, thumbnail_path: str):
        """Generate thumbnail for video"""
        try:
            # This would use ffmpeg or similar to extract video frame
            # For now, we'll create a placeholder
            with open(thumbnail_path, 'w') as f:
                f.write(f"Video thumbnail for {file_path}")
            
        except Exception as e:
            logger.error(f"Error generating video thumbnail: {str(e)}")
    
    def _generate_pdf_thumbnail(self, file_path: str, thumbnail_path: str):
        """Generate thumbnail for PDF"""
        try:
            # This would use PyPDF2 or similar to extract first page
            # For now, we'll create a placeholder
            with open(thumbnail_path, 'w') as f:
                f.write(f"PDF thumbnail for {file_path}")
            
        except Exception as e:
            logger.error(f"Error generating PDF thumbnail: {str(e)}")
    
    def _scan_virus(self, file_id: str, file_path: str):
        """Scan file for viruses"""
        try:
            # This would integrate with antivirus software
            # For now, we'll just log the scan
            logger.info(f"Virus scan completed for {file_id}")
            
        except Exception as e:
            logger.error(f"Error scanning file for viruses: {str(e)}")
    
    def _extract_metadata(self, file_id: str, file_path: str):
        """Extract metadata from file"""
        try:
            if file_id not in self.files:
                return
            
            file = self.files[file_id]
            
            # Extract basic metadata
            metadata = {
                'file_size': file.size,
                'mime_type': file.mime_type,
                'upload_date': file.upload_date.isoformat(),
                'file_type': file.file_type.value
            }
            
            # Extract type-specific metadata
            if file.file_type == FileType.IMAGE:
                metadata.update(self._extract_image_metadata(file_path))
            elif file.file_type == FileType.VIDEO:
                metadata.update(self._extract_video_metadata(file_path))
            elif file.file_type == FileType.AUDIO:
                metadata.update(self._extract_audio_metadata(file_path))
            
            # Update file metadata
            file.metadata = metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
    
    def _extract_image_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from image"""
        try:
            # This would use PIL or similar to extract image metadata
            return {
                'width': 1920,
                'height': 1080,
                'color_space': 'RGB',
                'format': 'JPEG'
            }
            
        except Exception as e:
            logger.error(f"Error extracting image metadata: {str(e)}")
            return {}
    
    def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from video"""
        try:
            # This would use ffmpeg or similar to extract video metadata
            return {
                'duration': 120.5,
                'width': 1920,
                'height': 1080,
                'fps': 30,
                'codec': 'H.264'
            }
            
        except Exception as e:
            logger.error(f"Error extracting video metadata: {str(e)}")
            return {}
    
    def _extract_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from audio"""
        try:
            # This would use mutagen or similar to extract audio metadata
            return {
                'duration': 180.2,
                'bitrate': 320,
                'sample_rate': 44100,
                'channels': 2
            }
            
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {str(e)}")
            return {}
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get file sharing analytics"""
        try:
            return {
                'total_files': len(self.files),
                'total_shares': len(self.shares),
                'total_size': sum(file.size for file in self.files.values()),
                'files_by_type': {
                    file_type.value: len([f for f in self.files.values() if f.file_type == file_type])
                    for file_type in FileType
                },
                'total_downloads': sum(file.download_count for file in self.files.values()),
                'active_shares': len([s for s in self.shares.values() if s.is_active])
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}

# Global file sharing system instance
file_sharing_system = FileSharingSystem()
