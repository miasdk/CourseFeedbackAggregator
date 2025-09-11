"""Base controller class with common patterns and utilities."""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging

from ..config.database import get_db


class BaseController:
    """Base controller class providing common functionality for all controllers.
    
    Provides:
    - Error handling patterns
    - Logging utilities
    - Common validation methods
    - Database session management
    - Standard response formatting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present and not None.
        
        Args:
            data: Dictionary of data to validate
            required_fields: List of field names that must be present
            
        Raises:
            ValueError: If any required field is missing or None
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    async def _log_operation(self, operation: str, details: Dict[str, Any] = None) -> None:
        """Log controller operations for audit and debugging.
        
        Args:
            operation: Description of the operation being performed
            details: Additional context information
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "controller": self.__class__.__name__,
            "operation": operation
        }
        
        if details:
            log_data.update(details)
            
        self.logger.info(f"Controller operation: {operation}", extra=log_data)
    
    async def _handle_db_error(self, error: Exception, operation: str) -> None:
        """Handle database errors with consistent logging and re-raising.
        
        Args:
            error: The database exception that occurred
            operation: Description of the failed operation
            
        Raises:
            The original exception after logging
        """
        self.logger.error(
            f"Database error in {operation}: {str(error)}",
            extra={
                "controller": self.__class__.__name__,
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
        raise error
    
    async def _format_success_response(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format a standardized success response.
        
        Args:
            data: The response data
            metadata: Optional metadata to include
            
        Returns:
            Formatted response dictionary
        """
        response = {
            "success": True,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response
    
    async def _format_error_response(self, error_message: str, error_code: str = None) -> Dict[str, Any]:
        """Format a standardized error response.
        
        Args:
            error_message: Human-readable error description
            error_code: Optional error code for client handling
            
        Returns:
            Formatted error response dictionary
        """
        response = {
            "success": False,
            "error": {
                "message": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if error_code:
            response["error"]["code"] = error_code
            
        return response
    
    async def _paginate_results(self, results: List[Any], page: int = 1, per_page: int = 50) -> Dict[str, Any]:
        """Apply pagination to results and return paginated response.
        
        Args:
            results: List of results to paginate
            page: Page number (1-indexed)
            per_page: Number of items per page
            
        Returns:
            Paginated response with metadata
        """
        total_items = len(results)
        total_pages = (total_items + per_page - 1) // per_page
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        paginated_results = results[start_index:end_index]
        
        return {
            "items": paginated_results,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }