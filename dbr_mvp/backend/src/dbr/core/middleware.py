# src/dbr/core/middleware.py
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from dbr.core.logging_config import get_logger, LogContext
import json


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    def __init__(self, app, logger_name: str = "api"):
        super().__init__(app)
        self.logger = get_logger(logger_name)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Extract user info if available (from JWT token)
        user_id = None
        organization_id = None
        
        # Try to extract user info from request state (set by auth middleware)
        if hasattr(request.state, 'user'):
            user_id = getattr(request.state.user, 'id', None)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        with LogContext(
            request_id=request_id,
            user_id=user_id,
            organization_id=organization_id,
            api_endpoint=str(request.url.path),
            http_method=request.method
        ):
            self.logger.info(f"Request started: {request.method} {request.url.path}", extra={
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None
            })
            
            # Process request
            try:
                response = await call_next(request)
                
                # Calculate duration
                duration_ms = round((time.time() - start_time) * 1000, 2)
                
                # Log response
                self.logger.info(f"Request completed: {request.method} {request.url.path}", extra={
                    "status_code": response.status_code,
                    "duration_ms": duration_ms
                })
                
                return response
                
            except Exception as e:
                # Calculate duration
                duration_ms = round((time.time() - start_time) * 1000, 2)
                
                # Log error
                self.logger.error(f"Request failed: {request.method} {request.url.path}", extra={
                    "error_message": str(e),
                    "duration_ms": duration_ms,
                    "status_code": 500
                })
                
                raise


class AuthLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging authentication events"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("auth")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is an auth-related endpoint
        is_auth_endpoint = any(path in str(request.url.path) for path in ['/login', '/logout', '/token'])
        
        if is_auth_endpoint:
            self.logger.info(f"Authentication request: {request.method} {request.url.path}", extra={
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent", "unknown")
            })
        
        response = await call_next(request)
        
        if is_auth_endpoint:
            if response.status_code == 200:
                self.logger.info(f"Authentication successful: {request.method} {request.url.path}")
            else:
                self.logger.warning(f"Authentication failed: {request.method} {request.url.path}", extra={
                    "status_code": response.status_code
                })
        
        return response


class DatabaseLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging database-related operations"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("database")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log database operations for specific endpoints
        db_endpoints = ['/workitems', '/schedules', '/organizations', '/users']
        
        if any(endpoint in str(request.url.path) for endpoint in db_endpoints):
            if request.method in ['POST', 'PUT', 'DELETE']:
                self.logger.info(f"Database operation: {request.method} {request.url.path}")
        
        response = await call_next(request)
        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive error logging"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger("errors")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            
            # Log client errors (4xx) and server errors (5xx)
            if response.status_code >= 400:
                self.logger.warning(f"HTTP Error: {response.status_code}", extra={
                    "api_endpoint": str(request.url.path),
                    "http_method": request.method,
                    "status_code": response.status_code,
                    "client_ip": request.client.host if request.client else None
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Unhandled exception: {str(e)}", extra={
                "api_endpoint": str(request.url.path),
                "http_method": request.method,
                "exception_type": type(e).__name__,
                "client_ip": request.client.host if request.client else None
            }, exc_info=True)
            
            raise


# Utility function to log business logic events
def log_business_event(event_type: str, details: dict = None, user_id: str = None, organization_id: str = None):
    """Log business logic events (work item creation, schedule changes, etc.)"""
    logger = get_logger("business")
    
    with LogContext(
        user_id=user_id,
        organization_id=organization_id,
        event_type=event_type
    ):
        logger.info(f"Business event: {event_type}", extra=details or {})


# Utility function to log security events
def log_security_event(event_type: str, details: dict = None, user_id: str = None, severity: str = "INFO"):
    """Log security-related events"""
    logger = get_logger("security")
    
    log_method = getattr(logger, severity.lower(), logger.info)
    
    with LogContext(
        user_id=user_id,
        event_type=event_type,
        severity=severity
    ):
        log_method(f"Security event: {event_type}", extra=details or {})