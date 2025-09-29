# Database Manager - Complete Database Abstraction Layer

import sqlite3
import psycopg2
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import threading
from contextlib import contextmanager

class DatabaseManager:
    """Complete database abstraction layer to replace all Frappe dependencies"""
    
    def __init__(self, db_type="sqlite", connection_string=None):
        self.db_type = db_type
        self.connection_string = connection_string or "erp_system.db"
        self.connection_pool = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self):
        """Get database connection"""
        thread_id = threading.get_ident()
        
        with self.lock:
            if thread_id not in self.connection_pool:
                if self.db_type == "sqlite":
                    self.connection_pool[thread_id] = sqlite3.connect(
                        self.connection_string, 
                        check_same_thread=False
                    )
                elif self.db_type == "postgresql":
                    self.connection_pool[thread_id] = psycopg2.connect(
                        self.connection_string
                    )
            
            return self.connection_pool[thread_id]
    
    @contextmanager
    def get_cursor(self):
        """Get database cursor with automatic cleanup"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = None):
        """Execute SQL query"""
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                self.get_connection().commit()
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute SQL query with multiple parameters"""
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, params_list)
                self.get_connection().commit()
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
    
    def fetch_one(self, query: str, params: tuple = None):
        """Fetch single row"""
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
    
    def fetch_all(self, query: str, params: tuple = None):
        """Fetch all rows"""
        try:
            with self.get_cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert record and return ID"""
        try:
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ', '.join(['?' if self.db_type == 'sqlite' else '%s'] * len(columns))
            
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            with self.get_cursor() as cursor:
                cursor.execute(query, values)
                self.get_connection().commit()
                return cursor.lastrowid if self.db_type == 'sqlite' else cursor.fetchone()[0]
        except Exception as e:
            self.logger.error(f"Insert error: {str(e)}")
            raise
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: tuple = None):
        """Update record"""
        try:
            columns = list(data.keys())
            values = list(data.values())
            set_clause = ', '.join([f"{col} = {'?' if self.db_type == 'sqlite' else '%s'}" for col in columns])
            
            query = f"UPDATE {table} SET {set_clause} WHERE {where}"
            params = tuple(values) + (where_params or ())
            
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                self.get_connection().commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Update error: {str(e)}")
            raise
    
    def delete(self, table: str, where: str, where_params: tuple = None):
        """Delete record"""
        try:
            query = f"DELETE FROM {table} WHERE {where}"
            
            with self.get_cursor() as cursor:
                cursor.execute(query, where_params or ())
                self.get_connection().commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Delete error: {str(e)}")
            raise
    
    def exists(self, table: str, where: str, where_params: tuple = None) -> bool:
        """Check if record exists"""
        try:
            query = f"SELECT 1 FROM {table} WHERE {where} LIMIT 1"
            result = self.fetch_one(query, where_params)
            return result is not None
        except Exception as e:
            self.logger.error(f"Exists check error: {str(e)}")
            return False
    
    def count(self, table: str, where: str = None, where_params: tuple = None) -> int:
        """Count records"""
        try:
            query = f"SELECT COUNT(*) FROM {table}"
            if where:
                query += f" WHERE {where}"
            
            result = self.fetch_one(query, where_params)
            return result[0] if result else 0
        except Exception as e:
            self.logger.error(f"Count error: {str(e)}")
            return 0
    
    def get_list(self, table: str, fields: List[str] = None, filters: Dict[str, Any] = None, 
                 order_by: str = None, limit: int = None, offset: int = None) -> List[Dict]:
        """Get list of records"""
        try:
            field_list = ', '.join(fields) if fields else '*'
            query = f"SELECT {field_list} FROM {table}"
            params = []
            
            if filters:
                where_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        placeholders = ', '.join(['?' if self.db_type == 'sqlite' else '%s'] * len(value))
                        where_conditions.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    else:
                        where_conditions.append(f"{key} = {'?' if self.db_type == 'sqlite' else '%s'}")
                        params.append(value)
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            if order_by:
                query += f" ORDER BY {order_by}"
            
            if limit:
                query += f" LIMIT {limit}"
                if offset:
                    query += f" OFFSET {offset}"
            
            results = self.fetch_all(query, tuple(params))
            
            # Convert to list of dictionaries
            if fields:
                return [dict(zip(fields, row)) for row in results]
            else:
                # Get column names
                with self.get_cursor() as cursor:
                    cursor.execute(f"PRAGMA table_info({table})" if self.db_type == 'sqlite' else 
                                  f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
                    columns = [row[0] for row in cursor.fetchall()]
                return [dict(zip(columns, row)) for row in results]
                
        except Exception as e:
            self.logger.error(f"Get list error: {str(e)}")
            return []
    
    def get_value(self, table: str, field: str, where: str, where_params: tuple = None):
        """Get single value"""
        try:
            query = f"SELECT {field} FROM {table} WHERE {where} LIMIT 1"
            result = self.fetch_one(query, where_params)
            return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Get value error: {str(e)}")
            return None
    
    def set_value(self, table: str, field: str, value: Any, where: str, where_params: tuple = None):
        """Set single value"""
        try:
            query = f"UPDATE {table} SET {field} = {'?' if self.db_type == 'sqlite' else '%s'} WHERE {where}"
            params = (value,) + (where_params or ())
            
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                self.get_connection().commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"Set value error: {str(e)}")
            raise
    
    def sql(self, query: str, params: tuple = None, as_dict: bool = False) -> List[Dict]:
        """Execute raw SQL query"""
        try:
            results = self.fetch_all(query, params)
            
            if as_dict and results:
                # Get column names from cursor description
                with self.get_cursor() as cursor:
                    cursor.execute(query, params)
                    columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in results]
            
            return results
        except Exception as e:
            self.logger.error(f"SQL error: {str(e)}")
            return []
    
    def commit(self):
        """Commit transaction"""
        try:
            self.get_connection().commit()
        except Exception as e:
            self.logger.error(f"Commit error: {str(e)}")
            raise
    
    def rollback(self):
        """Rollback transaction"""
        try:
            self.get_connection().rollback()
        except Exception as e:
            self.logger.error(f"Rollback error: {str(e)}")
            raise
    
    def close_all_connections(self):
        """Close all database connections"""
        with self.lock:
            for conn in self.connection_pool.values():
                try:
                    conn.close()
                except:
                    pass
            self.connection_pool.clear()

# Global database manager instance
db = DatabaseManager()

# Convenience functions to replace frappe.db
def sql(query, params=None, as_dict=False):
    """Execute SQL query"""
    return db.sql(query, params, as_dict)

def get_list(doctype, fields=None, filters=None, order_by=None, limit=None, offset=None):
    """Get list of records"""
    return db.get_list(doctype, fields, filters, order_by, limit, offset)

def get_value(doctype, field, filters=None):
    """Get single value"""
    if filters:
        where_conditions = []
        params = []
        for key, value in filters.items():
            where_conditions.append(f"{key} = {'?' if db.db_type == 'sqlite' else '%s'}")
            params.append(value)
        where_clause = " AND ".join(where_conditions)
        return db.get_value(doctype, field, where_clause, tuple(params))
    return None

def set_value(doctype, field, value, filters=None):
    """Set single value"""
    if filters:
        where_conditions = []
        params = []
        for key, val in filters.items():
            where_conditions.append(f"{key} = {'?' if db.db_type == 'sqlite' else '%s'}")
            params.append(val)
        where_clause = " AND ".join(where_conditions)
        return db.set_value(doctype, field, value, where_clause, tuple(params))
    return None

def exists(doctype, filters=None):
    """Check if record exists"""
    if filters:
        where_conditions = []
        params = []
        for key, value in filters.items():
            where_conditions.append(f"{key} = {'?' if db.db_type == 'sqlite' else '%s'}")
            params.append(value)
        where_clause = " AND ".join(where_conditions)
        return db.exists(doctype, where_clause, tuple(params))
    return False

def count(doctype, filters=None):
    """Count records"""
    if filters:
        where_conditions = []
        params = []
        for key, value in filters.items():
            where_conditions.append(f"{key} = {'?' if db.db_type == 'sqlite' else '%s'}")
            params.append(value)
        where_clause = " AND ".join(where_conditions)
        return db.count(doctype, where_clause, tuple(params))
    return db.count(doctype)
