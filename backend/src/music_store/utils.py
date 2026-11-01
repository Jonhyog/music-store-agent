def pagination_params(page: int, page_size: int) -> tuple[int, int]:
    """Return ``(limit, offset)`` for a 1-based ``page`` of ``page_size`` rows."""
    return page_size, (page - 1) * page_size


def is_numeric(value: str) -> bool:
    """True for a non-empty string of ASCII digits (no sign, spaces or decimals)."""
    return value.isascii() and value.isdigit()
