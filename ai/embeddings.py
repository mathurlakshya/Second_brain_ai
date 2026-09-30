from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def _get_model():
    # Lazy loading keeps application startup lightweight.
    return SentenceTransformer("all-MiniLM-L6-v2")


def create_embedding(text):
    if not text:
        return []
    return _get_model().encode(text).tolist()
