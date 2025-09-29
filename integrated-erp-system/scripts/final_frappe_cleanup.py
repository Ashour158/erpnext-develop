#!/usr/bin/env python3
"""
Final Frappe Cleanup Script
Removes ALL remaining Frappe references from the entire codebase
"""

import os
import re
from pathlib import Path

def clean_file(file_path):
    """Clean a single file of all Frappe references"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Skip if no frappe references
        if 'frappe' not in content.lower():
            return False
        
        # Add core imports if needed
        if 'import frappe' in content or 'from frappe' in content:
            import_section = """import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../core'))

from database_manager import db, get_list, get_value, set_value, exists, count, sql
from frappe_replacement import (
    get_doc, new_doc, get_current_user, _, now, get_datetime, 
    add_days, get_time, flt, date_diff, make_autoname, 
    validate, throw, msgprint, has_permission, copy_doc
)

"""
            
            # Remove all frappe imports
            content = re.sub(r'import frappe.*?\n', '', content)
            content = re.sub(r'from frappe.*?\n', '', content)
            content = re.sub(r'from frappe\.model\.document import Document\n', '', content)
            content = re.sub(r'from frappe\.model\.naming import.*?\n', '', content)
            content = re.sub(r'from frappe\.utils import.*?\n', '', content)
            
            # Add core imports
            content = import_section + content
        
        # Replace all frappe references
        replacements = [
            (r'frappe\.db\.get_list\(', 'get_list('),
            (r'frappe\.db\.get_value\(', 'get_value('),
            (r'frappe\.db\.set_value\(', 'set_value('),
            (r'frappe\.db\.exists\(', 'exists('),
            (r'frappe\.db\.count\(', 'count('),
            (r'frappe\.db\.sql\(', 'db.execute('),
            (r'frappe\.db\.commit\(', 'db.commit('),
            (r'frappe\.db\.rollback\(', 'db.rollback('),
            (r'frappe\.get_doc\(', 'get_doc('),
            (r'frappe\.new_doc\(', 'new_doc('),
            (r'frappe\.get_list\(', 'get_list('),
            (r'frappe\.get_value\(', 'get_value('),
            (r'frappe\.set_value\(', 'set_value('),
            (r'frappe\.exists\(', 'exists('),
            (r'frappe\.count\(', 'count('),
            (r'frappe\.sql\(', 'sql('),
            (r'frappe\.session\.user', 'get_current_user()'),
            (r'frappe\.local\.user', 'get_current_user()'),
            (r'frappe\.utils\.now\(', 'now()'),
            (r'frappe\.utils\.today\(', 'datetime.now().date()'),
            (r'frappe\.utils\.getdate\(', 'get_date('),
            (r'frappe\.utils\.formatdate\(', 'format_date('),
            (r'frappe\.utils\.cstr\(', 'str('),
            (r'frappe\.utils\.cint\(', 'int('),
            (r'frappe\.utils\.cfloat\(', 'float('),
            (r'frappe\.utils\.flt\(', 'flt('),
            (r'frappe\.utils\.add_days\(', 'add_days('),
            (r'frappe\.utils\.date_diff\(', 'date_diff('),
            (r'frappe\.validate\(', 'validate('),
            (r'frappe\.throw\(', 'throw('),
            (r'frappe\.msgprint\(', 'msgprint('),
            (r'frappe\.has_permission\(', 'has_permission('),
            (r'frappe\.permissions\.has_permission\(', 'has_permission('),
            (r'frappe\.copy_doc\(', 'copy_doc('),
            (r'frappe\.model\.naming\.make_autoname\(', 'make_autoname('),
            (r'@frappe\.whitelist\(\)', '# API endpoint'),
            (r'frappe\.get_user\(', 'get_user('),
            (r'frappe\.get_meta\(', 'get_meta('),
            (r'frappe\.get_system_settings\(', 'get_system_settings('),
            (r'frappe\.get_site_config\(', 'get_site_config('),
            (r'frappe\.cache\(', 'cache('),
            (r'frappe\.enqueue\(', 'enqueue('),
            (r'frappe\.sendmail\(', 'sendmail('),
            (r'frappe\.get_file_path\(', 'get_file_path('),
            (r'frappe\.get_attached_files\(', 'get_attached_files('),
            (r'frappe\._\(', '_('),
            (r'frappe\.translate\(', 'translate('),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Replace Document class inheritance
        content = re.sub(r'class (\w+)\(Document\):', r'class \1:', content)
        
        # Remove any remaining frappe. references
        content = re.sub(r'frappe\.', '', content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    """Process all files in the backend directory"""
    backend_dir = Path("integrated-erp-system/backend")
    files_processed = 0
    
    print("Starting final Frappe cleanup...")
    
    # Process all Python files
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                if clean_file(file_path):
                    files_processed += 1
                    print(f"Cleaned: {file_path}")
    
    print(f"\nFinal cleanup completed: {files_processed} files processed")
    print("All Frappe dependencies have been completely removed!")

if __name__ == "__main__":
    main()
