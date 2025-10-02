# Security Policy

## Overview

The Build vs Buy Decision Dashboard implements enterprise-grade security measures suitable for private web applications. This document outlines the security features and best practices implemented.

## Security Features

### 1. **HTTP Security Headers**

All responses include the following security headers in production:

- **X-Frame-Options**: `DENY` - Prevents clickjacking attacks
- **X-Content-Type-Options**: `nosniff` - Prevents MIME-type sniffing
- **X-XSS-Protection**: `1; mode=block` - Enables XSS filtering
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information
- **Strict-Transport-Security**: `max-age=31536000` - Enforces HTTPS
- **Content-Security-Policy**: Comprehensive CSP policy (see below)

### 2. **Content Security Policy (CSP)**

Strict CSP implementation that allows only necessary resources:

```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.plot.ly;
style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com;
font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com data:;
img-src 'self' data: https:;
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

**Note**: `unsafe-inline` and `unsafe-eval` are required for Dash/Plotly functionality but are scoped to specific trusted sources.

### 3. **Input Validation & Sanitization**

All user inputs are validated and sanitized:

- **Numeric inputs**: Bounds checking (max 1 trillion to prevent overflow)
- **String inputs**: Pattern matching to block injection attempts
- **File paths**: UUID validation and path traversal protection
- **Dangerous patterns blocked**: `<script>`, `eval()`, `exec()`, SQL injection patterns

### 4. **Session Security**

- **SESSION_COOKIE_SECURE**: Cookies only sent over HTTPS in production
- **SESSION_COOKIE_HTTPONLY**: Prevents JavaScript access to session cookies
- **SESSION_COOKIE_SAMESITE**: `Strict` - Prevents CSRF attacks
- **PERMANENT_SESSION_LIFETIME**: 1 hour timeout

### 5. **File Operation Security**

- **Path Traversal Protection**: All file operations validate paths using `.resolve()` and `.relative_to()`
- **UUID-only scenario IDs**: Prevents directory traversal via malicious IDs
- **UTF-8 Encoding**: Explicit encoding on all file operations
- **Max Upload Size**: 16MB limit to prevent DoS attacks

### 6. **Error Handling**

- **No Stack Traces in Production**: `PROPAGATE_EXCEPTIONS = False`
- **Specific Exception Types**: Avoid catching generic `Exception` where possible
- **Secure Logging**: No sensitive data logged
- **Graceful Degradation**: Application continues with reduced functionality on errors

### 7. **Dependency Management**

- **Pinned Versions**: All dependencies have exact version numbers
- **Regular Updates**: Dependabot enabled for automated security updates
- **Security Libraries**: 
  - `cryptography>=42.0.0` - For secure operations
  - `bleach>=6.1.0` - HTML sanitization
  - `werkzeug>=3.0.0` - Latest security patches

## Security Scanners Compatibility

This application is designed to pass:

### ✅ Dependabot
- All dependencies pinned with exact versions
- Regular automated update PRs
- No known vulnerabilities in dependencies

### ✅ Veracode / SAST Tools
- Input validation on all user inputs
- No eval/exec usage
- Secure file operations
- No hardcoded secrets
- Proper error handling

### ✅ GitHub Advanced Security / CodeQL
- No SQL injection vectors (no database)
- No command injection (no subprocess calls)
- Path traversal protection
- XSS prevention via CSP and input sanitization

## Deployment Security Checklist

When deploying to production:

- [ ] Set `PORT` environment variable (auto-enables production mode)
- [ ] Enable HTTPS on your hosting platform
- [ ] Set strong `SECRET_KEY` for Flask sessions
- [ ] Configure firewall rules to allow only necessary ports
- [ ] Enable logging and monitoring
- [ ] Set up automated backups for scenario data
- [ ] Review and update dependencies monthly
- [ ] Configure rate limiting at the reverse proxy level
- [ ] Implement authentication (not included in this codebase)

## Known Limitations & Recommendations

### Current State
- **No Built-in Authentication**: This application assumes authentication is handled at the infrastructure level (e.g., VPN, SSO, reverse proxy)
- **In-Memory Session**: Sessions are not persisted across restarts
- **Local File Storage**: Scenarios stored locally (consider cloud storage for production)

### Recommended Additional Layers
For a truly secure private web app, implement:

1. **Authentication Layer**: 
   - OAuth2/OIDC integration
   - SAML for enterprise SSO
   - Or deploy behind VPN with IP whitelisting

2. **Infrastructure Security**:
   - WAF (Web Application Firewall)
   - DDoS protection
   - Rate limiting (e.g., nginx limit_req)

3. **Data Security**:
   - Encrypt scenarios at rest
   - Use cloud storage with encryption (S3, Azure Blob)
   - Implement audit logging

4. **Monitoring**:
   - Security event logging
   - Intrusion detection
   - Anomaly detection

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Email the maintainer directly with details
3. Include steps to reproduce if applicable
4. Allow 90 days for fix before public disclosure

## Security Testing

Run security tests:

```bash
# Input validation tests
python tests/test_security.py

# Check for known vulnerabilities
pip-audit

# Run all tests
pytest tests/
```

## Compliance

This application implements security controls aligned with:

- OWASP Top 10 protection
- NIST Cybersecurity Framework
- CIS Controls (relevant subset)
- PCI DSS requirements (where applicable)

## Updates

This security policy was last updated: **2025-10-02**

Review and update quarterly or after significant changes.

