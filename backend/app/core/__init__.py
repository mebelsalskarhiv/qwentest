from app.core.config import settings


def get_allowed_origins():
    """Get allowed CORS origins."""
    return settings.allowed_origins_list
