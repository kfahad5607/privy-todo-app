import re
from fastapi import status

PG_FOREIGN_KEY_VIOLATION = '23503'
PG_UNIQUE_VIOLATION = '23505'

def extract_unique_violation_details(error_msg):
    """Extract constraint name and field name from unique violation error."""
    # Generic pattern to extract constraint name
    constraint_match = re.search(r'constraint\s+"([^"]+)"', error_msg)
    constraint_name = constraint_match.group(1) if constraint_match else "unknown"
    
    # Extract field name from constraint name
    # Convention: if constraint name is like "users_email_key", field name is "email"
    field_name = None
    if '_' in constraint_name:
        parts = constraint_name.split('_')
        if len(parts) >= 2 and parts[-1] == "key":
            field_name = parts[-2]  # Take the part before "_key"
    
    # Additional parsing for "Detail:" in asyncpg errors
    if field_name is None:
        detail_match = re.search(r'Detail:\s*Key\s*\(([^)]+)\)', error_msg)
        if detail_match:
            field_name = detail_match.group(1).split(',')[0].strip()
    
    return field_name or "unknown"

def extract_constraint_name(error_msg):
    """Extract constraint name from foreign key violation error."""
    constraint_match = re.search(r'constraint\s+"([^"]+)"', error_msg)
    return constraint_match.group(1) if constraint_match else "unknown"

class BaseAppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundException(BaseAppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class ValidationException(BaseAppException):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message, status_code=status_code)