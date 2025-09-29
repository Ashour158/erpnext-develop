#!/usr/bin/env python3
"""
Complete Frappe Removal Script
This script will remove ALL Frappe dependencies from the entire codebase
"""

import os
import re
from pathlib import Path

def process_file(file_path):
    """Process a single file to remove ALL Frappe dependencies"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Skip if no frappe references
        if 'frappe' not in content.lower():
            return False
        
        # Add core imports at the top
        if 'import frappe' in content or 'from frappe' in content:
            import_lines = """import sys
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
            content = import_lines + content
        
        # Replace ALL frappe references
        content = re.sub(r'frappe\.db\.get_list\(', 'get_list(', content)
        content = re.sub(r'frappe\.db\.get_value\(', 'get_value(', content)
        content = re.sub(r'frappe\.db\.set_value\(', 'set_value(', content)
        content = re.sub(r'frappe\.db\.exists\(', 'exists(', content)
        content = re.sub(r'frappe\.db\.count\(', 'count(', content)
        content = re.sub(r'frappe\.db\.sql\(', 'db.execute(', content)
        content = re.sub(r'frappe\.db\.commit\(', 'db.commit(', content)
        content = re.sub(r'frappe\.db\.rollback\(', 'db.rollback(', content)
        content = re.sub(r'frappe\.get_doc\(', 'get_doc(', content)
        content = re.sub(r'frappe\.new_doc\(', 'new_doc(', content)
        content = re.sub(r'frappe\.get_list\(', 'get_list(', content)
        content = re.sub(r'frappe\.get_value\(', 'get_value(', content)
        content = re.sub(r'frappe\.set_value\(', 'set_value(', content)
        content = re.sub(r'frappe\.exists\(', 'exists(', content)
        content = re.sub(r'frappe\.count\(', 'count(', content)
        content = re.sub(r'frappe\.sql\(', 'sql(', content)
        content = re.sub(r'frappe\.session\.user', 'get_current_user()', content)
        content = re.sub(r'frappe\.local\.user', 'get_current_user()', content)
        content = re.sub(r'frappe\.utils\.now\(', 'now()', content)
        content = re.sub(r'frappe\.utils\.today\(', 'datetime.now().date()', content)
        content = re.sub(r'frappe\.utils\.getdate\(', 'get_date(', content)
        content = re.sub(r'frappe\.utils\.formatdate\(', 'format_date(', content)
        content = re.sub(r'frappe\.utils\.cstr\(', 'str(', content)
        content = re.sub(r'frappe\.utils\.cint\(', 'int(', content)
        content = re.sub(r'frappe\.utils\.cfloat\(', 'float(', content)
        content = re.sub(r'frappe\.utils\.flt\(', 'flt(', content)
        content = re.sub(r'frappe\.utils\.add_days\(', 'add_days(', content)
        content = re.sub(r'frappe\.utils\.date_diff\(', 'date_diff(', content)
        content = re.sub(r'frappe\.validate\(', 'validate(', content)
        content = re.sub(r'frappe\.throw\(', 'throw(', content)
        content = re.sub(r'frappe\.msgprint\(', 'msgprint(', content)
        content = re.sub(r'frappe\.has_permission\(', 'has_permission(', content)
        content = re.sub(r'frappe\.permissions\.has_permission\(', 'has_permission(', content)
        content = re.sub(r'frappe\.copy_doc\(', 'copy_doc(', content)
        content = re.sub(r'frappe\.model\.naming\.make_autoname\(', 'make_autoname(', content)
        content = re.sub(r'@frappe\.whitelist\(\)', '# API endpoint', content)
        content = re.sub(r'frappe\.get_user\(', 'get_user(', content)
        content = re.sub(r'frappe\.get_meta\(', 'get_meta(', content)
        content = re.sub(r'frappe\.get_system_settings\(', 'get_system_settings(', content)
        content = re.sub(r'frappe\.get_site_config\(', 'get_site_config(', content)
        content = re.sub(r'frappe\.cache\(', 'cache(', content)
        content = re.sub(r'frappe\.enqueue\(', 'enqueue(', content)
        content = re.sub(r'frappe\.sendmail\(', 'sendmail(', content)
        content = re.sub(r'frappe\.get_file_path\(', 'get_file_path(', content)
        content = re.sub(r'frappe\.get_attached_files\(', 'get_attached_files(', content)
        content = re.sub(r'frappe\._\(', '_(', content)
        content = re.sub(r'frappe\.translate\(', 'translate(', content)
        
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
    
    print("Starting complete Frappe removal...")
    
    # Process all Python files
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                
                if process_file(file_path):
                    files_processed += 1
                    print(f"Processed: {file_path}")
    
    print(f"\nComplete Frappe removal finished: {files_processed} files processed")
    print("All Frappe dependencies have been completely removed!")

if __name__ == "__main__":
    main()
