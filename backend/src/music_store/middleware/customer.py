import sqlite3
from typing import Annotated

from anyio import to_thread
from fastapi import Depends, Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from music_store.models.customer import CustomerModel

CUSTOMER_HEADER = b"x-customer-id"

GET_CUSTOMER_QUERY = """
    SELECT customer_id, name, phone, email, city
    FROM customers
    WHERE customer_id = ?
"""


def _load_customer(database_path, customer_id: int) -> CustomerModel | None:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(GET_CUSTOMER_QUERY, (customer_id,)).fetchone()
    finally:
        conn.close()
    return CustomerModel(**row) if row else None


class CustomerMiddleware:
    """Resolves `x-customer-id` into `request.state.customer` (None means Visitor)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw = dict(scope["headers"]).get(CUSTOMER_HEADER)
        customer: CustomerModel | None = None
        if raw is not None:
            value = raw.decode("latin-1").strip()
            if not (value.isascii() and value.isdigit()):
                await self._reject(scope, receive, send, "Malformed x-customer-id header.")
                return
            database_path = scope["app"].state.settings.database_path
            customer = await to_thread.run_sync(_load_customer, database_path, int(value))
            if customer is None:
                await self._reject(scope, receive, send, "Unknown customer.")
                return

        scope.setdefault("state", {})["customer"] = customer
        await self.app(scope, receive, send)

    @staticmethod
    async def _reject(scope: Scope, receive: Receive, send: Send, detail: str) -> None:
        await JSONResponse({"detail": detail}, status_code=400)(scope, receive, send)


def get_current_customer(request: Request) -> CustomerModel | None:
    return request.state.customer


CurrentCustomer = Annotated[CustomerModel | None, Depends(get_current_customer)]
