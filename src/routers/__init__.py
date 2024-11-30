from .task import router as task_router
from .user import router as user_router
from .auth import router as auth_router

__all__ = ["user_router", "task_router", "auth_router"]
