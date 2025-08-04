"""
Configuration file for Component Data Processor

This file contains all configuration settings for the component data processing script.
Modify these settings according to your environment and requirements.
"""

import os
from pathlib import Path

# =============================================================================
# FILE PATHS CONFIGURATION
# =============================================================================

# Path to the Master BOM file (Excel format)
# This should be the reference file containing all component data with status information
MASTER_BOM_PATH = "Master_BOM_Real.xlsx"

# Output directory for processed files
# All generated files will be saved in this directory
OUTPUT_DIR = "output"

# =============================================================================
# COLUMN MAPPING CONFIGURATION
# =============================================================================

# Column mapping for standardizing column names
# Maps expected column names to actual column names in your files
COLUMN_MAPPING = {
    'PN': 'PN',                    # Part Number
    'Project': 'Project',          # Project identifier
    'Price': 'Price',              # Component price
    'Supplier': 'Supplier',        # Supplier name
    'Description': 'Description',  # Component description
    'Status': 'Status'             # Component status (D, 0, X, NaN)
}

# Required columns that must be present and non-empty for processing
# Rows missing these values will be excluded during cleaning
REQUIRED_COLUMNS = ['PN', 'Project']

# =============================================================================
# DATA CLEANING CONFIGURATION
# =============================================================================

# Columns that should be treated as text and cleaned (trimmed, normalized)
TEXT_COLUMNS = ['PN', 'Project', 'Supplier', 'Description']

# Whether to convert text to uppercase during cleaning
CONVERT_TO_UPPERCASE = False

# Whether to remove non-ASCII characters during text normalization
REMOVE_NON_ASCII = True

# =============================================================================
# PROCESSING CONFIGURATION
# =============================================================================

# Status values and their meanings:
# 'D' = Deprecated (will be updated to 'X')
# '0' = Duplicate/uncertain match (requires manual verification)
# 'X' = Already marked as old (will be skipped)
# NaN/null = Unknown component (potential new entry)

STATUS_MAPPINGS = {
    'DEPRECATED': 'D',
    'DUPLICATE': '0',
    'OLD': 'X',
    'UNKNOWN': None  # Represents NaN/null values
}

# =============================================================================
# OUTPUT CONFIGURATION
# =============================================================================

# Whether to save excluded rows to a separate file
SAVE_EXCLUDED_ROWS = True

# Whether to save an updated Master BOM file
SAVE_UPDATED_MASTER_BOM = True

# Whether to generate a summary report
GENERATE_SUMMARY_REPORT = True

# File naming patterns (use strftime format codes)
OUTPUT_FILE_PATTERN = "Update_{timestamp}.xlsx"
EXCLUDED_FILE_PATTERN = "Clean_Excluded_{timestamp}.xlsx"
MASTER_BOM_OUTPUT_PATTERN = "Master_BOM_Updated_{timestamp}.xlsx"
SUMMARY_REPORT_PATTERN = "Processing_Summary_{timestamp}.csv"
LOG_FILE_PATTERN = "component_processor_{timestamp}.log"

# =============================================================================
# EXCEL FORMATTING CONFIGURATION
# =============================================================================

# Colors for highlighting rows in the output Excel file
HIGHLIGHT_COLORS = {
    'DUPLICATE': 'FFCCCC',    # Light red for duplicates/unknowns
    'UPDATED': 'FFFFCC',      # Light yellow for updates
    'SKIPPED': 'E6E6E6'       # Light gray for skipped items
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = 'INFO'

# Whether to log to console in addition to file
LOG_TO_CONSOLE = True

# =============================================================================
# EMAIL CONFIGURATION (Optional)
# =============================================================================

# Email settings for sending processed files (if needed)
EMAIL_ENABLED = False
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_USERNAME = ""  # Set your email username
EMAIL_PASSWORD = ""  # Set your email password or app password
EMAIL_RECIPIENTS = []  # List of recipient email addresses

# =============================================================================
# ADVANCED CONFIGURATION
# =============================================================================

# Maximum number of rows to process in a single batch
MAX_BATCH_SIZE = 10000

# Whether to create backup of Master BOM before updating
CREATE_MASTER_BOM_BACKUP = True

# Timeout for file operations (in seconds)
FILE_OPERATION_TIMEOUT = 300

# =============================================================================
# VALIDATION CONFIGURATION
# =============================================================================

# Patterns for validating part numbers (regex)
PN_VALIDATION_PATTERN = r'^[A-Z0-9\-_]+$'

# Maximum length for part numbers
MAX_PN_LENGTH = 50

# Maximum length for project names
MAX_PROJECT_LENGTH = 100

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_timestamp_format():
    """Return the timestamp format used for file naming."""
    return "%Y-%m-%d"

def get_detailed_timestamp_format():
    """Return the detailed timestamp format used for logging."""
    return "%Y%m%d_%H%M%S"

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check if Master BOM path exists
    if not os.path.exists(MASTER_BOM_PATH):
        errors.append(f"Master BOM file not found: {MASTER_BOM_PATH}")
    
    # Check required columns
    if not REQUIRED_COLUMNS:
        errors.append("REQUIRED_COLUMNS cannot be empty")
    
    # Validate output directory
    try:
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
    except Exception as e:
        errors.append(f"Cannot create output directory: {e}")
    
    return errors

# =============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# =============================================================================

# Override settings based on environment variables
if os.getenv('COMPONENT_PROCESSOR_ENV') == 'production':
    LOG_LEVEL = 'WARNING'
    CREATE_MASTER_BOM_BACKUP = True
elif os.getenv('COMPONENT_PROCESSOR_ENV') == 'development':
    LOG_LEVEL = 'DEBUG'
    MAX_BATCH_SIZE = 100  # Smaller batches for testing
