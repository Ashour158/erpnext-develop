#!/usr/bin/env python3
"""
Complete Frappe Dependency Removal Script
Replaces all frappe.db references with independent database connection
"""

import os
import re
import sys
from pathlib import Path

def replace_frappe_references():
    """Replace all Frappe references in the codebase"""
    
    # Define replacement patterns
    replacements = {
        # Database operations
        r'frappe\.db\.get_list\(': 'get_list(',
        r'frappe\.db\.get_value\(': 'get_value(',
        r'frappe\.db\.set_value\(': 'set_value(',
        r'frappe\.db\.exists\(': 'exists(',
        r'frappe\.db\.count\(': 'count(',
        r'frappe\.db\.sql\(': 'sql(',
        r'frappe\.db\.execute\(': 'db.execute(',
        r'frappe\.db\.commit\(': 'db.commit(',
        r'frappe\.db\.rollback\(': 'db.rollback(',
        
        # Document operations
        r'frappe\.get_doc\(': 'get_doc(',
        r'frappe\.new_doc\(': 'new_doc(',
        r'frappe\.get_list\(': 'get_list(',
        r'frappe\.get_value\(': 'get_value(',
        r'frappe\.set_value\(': 'set_value(',
        r'frappe\.exists\(': 'exists(',
        r'frappe\.count\(': 'count(',
        r'frappe\.sql\(': 'sql(',
        
        # User operations
        r'frappe\.get_user\(': 'get_user(',
        r'frappe\.session\.user': 'get_current_user()',
        r'frappe\.local\.user': 'get_current_user()',
        
        # Date operations
        r'frappe\.utils\.now\(': 'datetime.now()',
        r'frappe\.utils\.today\(': 'datetime.now().date()',
        r'frappe\.utils\.getdate\(': 'get_date(',
        r'frappe\.utils\.formatdate\(': 'format_date(',
        
        # String operations
        r'frappe\.utils\.cstr\(': 'str(',
        r'frappe\.utils\.cint\(': 'int(',
        r'frappe\.utils\.cfloat\(': 'float(',
        r'frappe\.utils\.flt\(': 'float(',
        
        # Validation
        r'frappe\.validate\(': 'validate(',
        r'frappe\.throw\(': 'throw(',
        r'frappe\.msgprint\(': 'msgprint(',
        
        # Permissions
        r'frappe\.has_permission\(': 'has_permission(',
        r'frappe\.permissions\.has_permission\(': 'has_permission(',
        
        # Hooks and events
        r'frappe\.hooks\(': 'hooks(',
        r'frappe\.events\(': 'events(',
        
        # Cache
        r'frappe\.cache\(': 'cache(',
        r'frappe\.cache\.get\(': 'cache.get(',
        r'frappe\.cache\.set\(': 'cache.set(',
        r'frappe\.cache\.delete\(': 'cache.delete(',
        
        # Queue
        r'frappe\.enqueue\(': 'enqueue(',
        r'frappe\.queue\(': 'queue(',
        
        # Email
        r'frappe\.sendmail\(': 'sendmail(',
        r'frappe\.email\(': 'email(',
        
        # File operations
        r'frappe\.get_file_path\(': 'get_file_path(',
        r'frappe\.get_attached_files\(': 'get_attached_files(',
        
        # Translation
        r'frappe\._\(': '_(',
        r'frappe\.translate\(': 'translate(',
        
        # Other common patterns
        r'frappe\.get_meta\(': 'get_meta(',
        r'frappe\.get_system_settings\(': 'get_system_settings(',
        r'frappe\.get_site_config\(': 'get_site_config(',
    }
    
    # Files to process
    backend_dir = Path("integrated-erp-system/backend")
    files_processed = 0
    total_replacements = 0
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.tsx')):
                file_path = Path(root) / file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply all replacements
                    for pattern, replacement in replacements.items():
                        content = re.sub(pattern, replacement, content)
                    
                    # Additional specific replacements
                    content = re.sub(r'import frappe', 'from core.database_manager import *', content)
                    content = re.sub(r'from frappe import', 'from core.database_manager import', content)
                    content = re.sub(r'frappe\.', '', content)
                    
                    # Write back if changed
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        files_processed += 1
                        changes = len(re.findall(r'frappe\.', original_content))
                        total_replacements += changes
                        
                        print(f"Processed: {file_path} ({changes} replacements)")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    print(f"\nCompleted: {files_processed} files processed, {total_replacements} total replacements")

if __name__ == "__main__":
    replace_frappe_references()
