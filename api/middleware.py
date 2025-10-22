"""
Custom middleware
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests with timing
    """
    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}s"
            )
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware
    For production, use django-ratelimit or Redis-based solution
    """
    def process_request(self, request):
        # Implement rate limiting logic here
        # This is a placeholder
        return None
