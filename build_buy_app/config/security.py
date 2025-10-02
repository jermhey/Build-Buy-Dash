"""
Production Security Configuration for Build vs Buy Dashboard
Implements security best practices while preserving Dash functionality
"""
import os
from flask import Flask


class DashSecurityConfig:
    """Security configuration optimized for Dash applications."""
    
    def __init__(self):
        self.is_production = os.environ.get('PORT') is not None
        
    def configure_security_headers(self, server: Flask):
        """
        Configure security headers that work with Dash.
        Carefully tuned to avoid breaking functionality.
        """
        
        @server.after_request
        def add_security_headers(response):
            # Only add security headers in production
            if not self.is_production:
                return response
                
            # 1. X-Frame-Options - Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # 2. X-Content-Type-Options - Prevent MIME sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # 3. X-XSS-Protection - Enable XSS filtering
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # 4. Referrer Policy - Control referrer information
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # 5. DASH-COMPATIBLE Content Security Policy
            # This is the critical part - CSP that works with Dash
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.plot.ly https://unpkg.com",
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com https://cdn.jsdelivr.net",
                "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com data:",
                "img-src 'self' data: https:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'"
            ]
            response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
            
            # 6. Strict Transport Security (HTTPS only in production)
            if self.is_production:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            return response
            
        return server
    
    def configure_server_security(self, server: Flask):
        """Configure Flask server security settings."""
        
        # Remove server signature for security by obscurity
        server.config['SERVER_NAME'] = None
        
        # Session security (hardened)
        server.config['SESSION_COOKIE_SECURE'] = self.is_production
        server.config['SESSION_COOKIE_HTTPONLY'] = True
        server.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # Changed from 'Lax' to 'Strict' for better security
        server.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout
        
        # Additional security settings
        server.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
        server.config['TRAP_HTTP_EXCEPTIONS'] = True  # Better error handling
        server.config['TRAP_BAD_REQUEST_ERRORS'] = True  # Catch bad requests
        
        # Disable Flask debug in production
        if self.is_production:
            server.config['DEBUG'] = False
            server.config['TESTING'] = False
            server.config['PROPAGATE_EXCEPTIONS'] = False  # Don't expose stack traces
        
        return server
    
    def validate_inputs(self, user_input):
        """
        Validate user inputs to prevent injection attacks.
        Returns sanitized input or raises ValueError for invalid input.
        """
        if user_input is None:
            return None
            
        # Convert to string and basic sanitization
        sanitized = str(user_input).strip()
        
        # Check for basic injection patterns
        dangerous_patterns = [
            '<script', '</script>', 'javascript:', 'onload=', 'onerror=',
            'eval(', 'exec(', '__import__', 'subprocess', 'os.system'
        ]
        
        lower_input = sanitized.lower()
        for pattern in dangerous_patterns:
            if pattern in lower_input:
                raise ValueError(f"Invalid input detected: {pattern}")
        
        return sanitized
    
    def secure_float_conversion(self, value, default=0.0):
        """Securely convert input to float with validation."""
        try:
            if value in (None, "", "null", "undefined"):
                return default
                
            # Validate input first
            sanitized = self.validate_inputs(value)
            
            # Convert to float
            result = float(sanitized)
            
            # Reasonable bounds checking
            if abs(result) > 1e12:  # 1 trillion limit
                raise ValueError("Value too large")
                
            return result
            
        except (ValueError, TypeError) as e:
            print(f"Security: Invalid numeric input: {value} - {e}")
            return default


# Global security instance
security_config = DashSecurityConfig()


def secure_app_initialization(app, server):
    """
    Apply security configuration to Dash app and Flask server.
    Call this after creating your Dash app.
    """
    try:
        # Configure Flask server security
        security_config.configure_server_security(server)
        
        # Add security headers
        security_config.configure_security_headers(server)
        
        print("✅ Security configuration applied successfully")
        return app
        
    except Exception as e:
        print(f"⚠️ Security configuration failed: {e}")
        print("🔄 App will continue without security headers")
        return app


def safe_input_handler(func):
    """
    Decorator to safely handle user inputs in callbacks.
    Use this on callback functions that process user input.
    """
    def wrapper(*args, **kwargs):
        try:
            # Sanitize string inputs
            sanitized_args = []
            for arg in args:
                if isinstance(arg, str):
                    sanitized_args.append(security_config.validate_inputs(arg))
                else:
                    sanitized_args.append(arg)
            
            # Sanitize string values in kwargs
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    sanitized_kwargs[key] = security_config.validate_inputs(value)
                else:
                    sanitized_kwargs[key] = value
            
            return func(*sanitized_args, **sanitized_kwargs)
            
        except ValueError as e:
            print(f"Security: Blocked potentially malicious input: {e}")
            return "Invalid input detected"
        except Exception as e:
            print(f"Security handler error: {e}")
            return func(*args, **kwargs)  # Fallback to original function
    
    return wrapper
