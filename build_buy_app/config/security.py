"""
Security Configuration for Build vs Buy Dashboard
Contains security settings and constants
"""

# Security constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file uploads
MAX_SCENARIOS = 100  # Maximum scenarios per user
MAX_STRING_LENGTH = 1000  # Maximum string field length
MAX_NUMERIC_VALUE = 1e12  # Maximum numeric value (1 trillion)

# Input validation patterns
SAFE_FILENAME_PATTERN = r'^[a-zA-Z0-9\-_\.]+$'
SAFE_NAME_PATTERN = r'^[a-zA-Z0-9\s\-_\.]+$'

# Rate limiting settings (for future implementation)
RATE_LIMIT_REQUESTS = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Session security
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SECURE_RANDOM_BYTES = 32

# Content Security Policy - Updated to allow required CDNs for UI styling
CSP_POLICY = {
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
    'style-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net", 
    'font-src': "'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
    'img-src': "'self' data:",
    'connect-src': "'self'"
}

# Security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

# Logging configuration for security events
SECURITY_LOG_EVENTS = [
    'invalid_input',
    'file_upload_attempt',
    'large_request',
    'suspicious_activity'
]
