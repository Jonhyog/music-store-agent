def pagination_params(page: int, page_size: int) -> tuple[int, int]:
    """Return ``(limit, offset)`` for a 1-based ``page`` of ``page_size`` rows."""
    return page_size, (page - 1) * page_size
