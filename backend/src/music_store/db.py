import sqlite3
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(request.app.state.settings.database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


Db = Annotated[sqlite3.Connection, Depends(get_db)]
