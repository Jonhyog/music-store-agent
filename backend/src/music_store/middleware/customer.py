import sqlite3
from pathlib import Path
from typing import Annotated

from anyio import to_thread
from fastapi import Depends, Request
from starlette.types import ASGIApp, Receive, Scope, Send

from music_store.errors import MalformedCustomerIdError, UnknownCustomerError
from music_store.middleware.errors import error_response
from music_store.models.customer import CustomerModel
from music_store.utils import is_numeric

CUSTOMER_HEADER = b"x-customer-id"

GET_CUSTOMER_QUERY = """
    SELECT customer_id, name, phone, email, city
    FROM customers
    WHERE customer_id = ?
"""


def _load_customer(database_path: Path, customer_id: int) -> CustomerModel | None:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(GET_CUSTOMER_QUERY, (customer_id,)).fetchone()
    finally:
        conn.close()
    return CustomerModel(**row) if row else None


async def _resolve_customer(scope: Scope) -> CustomerModel | None:
    """Return the Customer named by the header, or None (Visitor) when it is absent.

    Raises a DomainError for a malformed or unknown id.
    """
    raw = dict(scope["headers"]).get(CUSTOMER_HEADER)
    if raw is None:
        return None
    value = raw.decode("latin-1").strip()
    if not is_numeric(value):
        raise MalformedCustomerIdError
    database_path = scope["app"].state.settings.database_path
    customer = await to_thread.run_sync(_load_customer, database_path, int(value))
    if customer is None:
        raise UnknownCustomerError
    return customer


class CustomerMiddleware:
    """Resolves `x-customer-id` into `request.state.customer` (None means Visitor)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            customer = await _resolve_customer(scope)
        except Exception as error:
            response = error_response(error)
        else:
            scope.setdefault("state", {})["customer"] = customer
            await self.app(scope, receive, send)
            return
        await response(scope, receive, send)


def get_current_customer(request: Request) -> CustomerModel | None:
    return request.state.customer


CurrentCustomer = Annotated[CustomerModel | None, Depends(get_current_customer)]
