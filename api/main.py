"""
Main API instance
Django Ninja API configuration
"""
from ninja import NinjaAPI
from ninja.security import HttpBearer
from django.http import HttpRequest
from apps.users.models import User

class AuthBearer(HttpBearer):
    """
    Simple Bearer token authentication
    For production, use JWT or OAuth2
    """
    def authenticate(self, request: HttpRequest, token: str):
        # This is a simple example - implement proper JWT authentication
        try:
            # For now, just check if user is authenticated via session
            if request.user.is_authenticated:
                return request.user
        except Exception:
            pass
        return None


# Create API instance
api = NinjaAPI(
    title="Operis Base System API",
    version="1.0.0",
    description="Full-stack RBAC system with Django Ninja and Next.js",
    docs_url="/docs",
    csrf=False,  # Disable CSRF for API (use proper auth instead)
)


# Health check endpoint
@api.get("/health", tags=["System"], auth=None)
def health_check(request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Operis Base System"
    }


# Import and register routers
from apps.rbac.api import router as rbac_router
from apps.users.api import router as users_router
from apps.seafood.api import router as seafood_router

api.add_router("/rbac/", rbac_router)
api.add_router("/users/", users_router)
api.add_router("/seafood/", seafood_router)


# Global exception handler
@api.exception_handler(Exception)
def global_exception_handler(request, exc):
    """Handle all uncaught exceptions"""
    import traceback
    error_detail = str(exc)

    # Log the error
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {error_detail}")
    logger.error(traceback.format_exc())

    return api.create_response(
        request,
        {"error": "Internal server error", "detail": error_detail},
        status=500,
    )
