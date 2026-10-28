from database.database import get_recent_memories


def get_recent_memories_for_user(user_id, limit=50):
    """Compatibility helper that always scopes results to one user."""
    return get_recent_memories(user_id=user_id, limit=limit)
