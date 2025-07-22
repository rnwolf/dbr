# frontend/exceptions.py
"""Custom exceptions for the frontend application"""


class APIError(Exception):
    """Base exception for API-related errors"""
    
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(APIError):
    """Exception raised when authentication fails"""
    
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)


class NetworkError(APIError):
    """Exception raised when network operations fail"""
    
    def __init__(self, message="Network error occurred"):
        super().__init__(message)


class ValidationError(APIError):
    """Exception raised when data validation fails"""
    
    def __init__(self, message="Validation error"):
        super().__init__(message, status_code=422)