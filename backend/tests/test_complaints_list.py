import sqlite3

COMPLAINT_KEYS = {
    "complaint_id",
    "customer_id",
    "customer_name",
    "order_id",
    "category",
    "description",
    "conversation_id",
    "created_at",
}


def _insert(settings, rows: list[tuple[int, int | None, str]]) -> None:
    """Insert (customer_id, order_id, created_at) complaints, one per minute apart as given."""
    conn = sqlite3.connect(settings.database_path)
    try:
        conn.executemany(
            "INSERT INTO complaints (customer_id, order_id, category, description,"
            " conversation_id, created_at) VALUES (?, ?, 'delivery', ?, 'conv', ?)",
            [(cid, oid, f"d-{at}", at) for cid, oid, at in rows],
        )
        conn.commit()
    finally:
        conn.close()


def _customer_name(settings, customer_id: int) -> str:
    conn = sqlite3.connect(settings.database_path)
    try:
        return conn.execute(
            "SELECT name FROM customers WHERE customer_id = ?", (customer_id,)
        ).fetchone()[0]
    finally:
        conn.close()


def test_empty_when_no_complaints(client):
    body = client.get("/complaints").json()
    assert body == {"complaints": [], "page": 1, "total": 0}


def test_item_shape_with_customer_name_and_nullable_order(client, settings):
    _insert(settings, [(3, 1, "2026-01-01T10:00:00+00:00"), (4, None, "2026-01-01T11:00:00+00:00")])
    items = client.get("/complaints").json()["complaints"]
    assert set(items[0]) == COMPLAINT_KEYS
    assert items[0]["order_id"] is None
    assert items[0]["customer_name"] == _customer_name(settings, 4)
    assert items[1]["order_id"] == 1


def test_newest_first(client, settings):
    _insert(
        settings,
        [
            (3, None, "2026-01-01T10:00:00+00:00"),
            (3, None, "2026-01-03T10:00:00+00:00"),
            (3, None, "2026-01-02T10:00:00+00:00"),
        ],
    )
    items = client.get("/complaints").json()["complaints"]
    assert [i["created_at"][:10] for i in items] == ["2026-01-03", "2026-01-02", "2026-01-01"]


def test_pagination(client, settings):
    _insert(settings, [(3, None, f"2026-01-0{d}T10:00:00+00:00") for d in range(1, 6)])
    first = client.get("/complaints", params={"page": 1, "pageSize": 2}).json()
    last = client.get("/complaints", params={"page": 3, "pageSize": 2}).json()
    assert first["total"] == 5
    assert len(first["complaints"]) == 2
    assert len(last["complaints"]) == 1
    assert last["page"] == 3
    assert not {c["complaint_id"] for c in first["complaints"]} & {
        c["complaint_id"] for c in last["complaints"]
    }
    assert client.get("/complaints", params={"page": 9}).json()["complaints"] == []


def test_filter_by_customer(client, settings):
    _insert(
        settings,
        [
            (3, None, "2026-01-01T10:00:00+00:00"),
            (4, None, "2026-01-02T10:00:00+00:00"),
            (3, None, "2026-01-03T10:00:00+00:00"),
        ],
    )
    body = client.get("/complaints", params={"customerId": 3}).json()
    assert body["total"] == 2
    assert {c["customer_id"] for c in body["complaints"]} == {3}


def test_unknown_customer_returns_empty(client, settings):
    _insert(settings, [(3, None, "2026-01-01T10:00:00+00:00")])
    body = client.get("/complaints", params={"customerId": 99999}).json()
    assert body == {"complaints": [], "page": 1, "total": 0}


def test_customer_header_is_ignored(client, settings):
    _insert(
        settings,
        [(3, None, "2026-01-01T10:00:00+00:00"), (4, None, "2026-01-02T10:00:00+00:00")],
    )
    body = client.get("/complaints", headers={"x-customer-id": "3"}).json()
    assert body["total"] == 2


def test_invalid_pagination_is_rejected(client):
    for params in ({"page": 0}, {"pageSize": 0}, {"pageSize": 101}, {"customerId": "x"}):
        assert client.get("/complaints", params=params).status_code == 422
