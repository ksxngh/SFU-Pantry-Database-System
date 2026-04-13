"""
SFU Food Pantry Management System - Configuration
Configure your database and application settings here
"""

import os
from datetime import timedelta

# ============================================
# Flask Configuration
# ============================================

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', False)
    TESTING = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# ============================================
# Database Configuration
# ============================================

# SQL Server Configuration
DB_CONFIG_SQLSERVER = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': os.environ.get('DB_SERVER', 'localhost'),
    'database': os.environ.get('DB_NAME', 'FoodPantry'),
    'trusted_connection': 'yes',
}

# MySQL Configuration
DB_CONFIG_MYSQL = {
    'driver': '{MySQL ODBC Driver}',
    'server': os.environ.get('DB_SERVER', 'localhost'),
    'database': os.environ.get('DB_NAME', 'FoodPantry'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port': os.environ.get('DB_PORT', '3306'),
}

# Choose which database to use
DB_TYPE = os.environ.get('DB_TYPE', 'sqlserver')  # 'sqlserver' or 'mysql'
DB_CONFIG = DB_CONFIG_SQLSERVER if DB_TYPE == 'sqlserver' else DB_CONFIG_MYSQL

# ============================================
# Application Settings
# ============================================

# Pagination
ITEMS_PER_PAGE = 20
DONATIONS_PER_PAGE = 10
VISITS_PER_PAGE = 15

# Warnings
EXPIRY_WARNING_DAYS = 7  # Days before expiration to show warnings
REORDER_WARNING_PERCENTAGE = 20  # Percentage below threshold to show warnings

# Date format
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DISPLAY_DATE_FORMAT = '%B %d, %Y'
DISPLAY_DATETIME_FORMAT = '%B %d, %Y at %I:%M %p'

# ============================================
# Feature Flags
# ============================================

FEATURES = {
    'ENABLE_DONATIONS': True,
    'ENABLE_VISITS': True,
    'ENABLE_DISTRIBUTION': True,
    'ENABLE_REPORTS': True,
    'ENABLE_EXPORT': True,
    'ENABLE_PHOTO_UPLOAD': False,
    'ENABLE_EMAIL_NOTIFICATIONS': False,
}

# ============================================
# Logging Configuration
# ============================================

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'foodpantry.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# ============================================
# Email Configuration (for future notifications)
# ============================================

EMAIL_CONFIG = {
    'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
    'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', True),
    'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
    'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'pantry@sfu.ca'),
}

# ============================================
# Security Configuration
# ============================================

SECURITY_CONFIG = {
    'PASSWORD_MIN_LENGTH': 8,
    'PASSWORD_REQUIRE_UPPERCASE': True,
    'PASSWORD_REQUIRE_NUMBERS': True,
    'PASSWORD_REQUIRE_SPECIAL': False,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 15,  # minutes
}

# ============================================
# Constants
# ============================================

VISITOR_TYPES = [
    'Student',
    'Community',
    'Staff',
    'Faculty',
    'Other'
]

DONOR_TYPES = [
    'Individual',
    'Organization',
    'Business',
    'Church',
    'Other'
]

USER_ROLES = [
    'Administrator',
    'Manager',
    'Volunteer',
    'Staff'
]
