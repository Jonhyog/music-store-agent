import csv

from music_store.settings import REPO_ROOT


def _csv(name):
    with open(REPO_ROOT / "data" / f"{name}.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_lists_first_page_with_total(client):
    total = len(_csv("customers"))
    body = client.get("/customers", params={"page": 1, "pageSize": 10}).json()
    assert body["page"] == 1
    assert body["total"] == total
    assert len(body["customers"]) == 10
    assert set(body["customers"][0]) == {
        "customer_id",
        "name",
        "phone",
        "email",
        "city",
        "order_count",
    }


def test_pages_do_not_overlap_and_last_page_is_partial(client):
    total = len(_csv("customers"))
    first = client.get("/customers", params={"page": 1, "pageSize": 20}).json()
    last = client.get("/customers", params={"page": 3, "pageSize": 20}).json()
    assert len(last["customers"]) == total - 40
    ids_first = {c["customer_id"] for c in first["customers"]}
    assert not ids_first & {c["customer_id"] for c in last["customers"]}


def test_page_past_the_end_is_empty(client):
    body = client.get("/customers", params={"page": 99, "pageSize": 20}).json()
    assert body["customers"] == []


def test_order_count_matches_orders(client):
    expected: dict[str, int] = {}
    for order in _csv("orders"):
        expected[order["customer_id"]] = expected.get(order["customer_id"], 0) + 1
    two_orders = next(cid for cid, n in expected.items() if n == 2)
    no_orders = next(
        c["customer_id"] for c in _csv("customers") if c["customer_id"] not in expected
    )

    body = client.get("/customers", params={"page": 1, "pageSize": 100}).json()
    counts = {str(c["customer_id"]): c["order_count"] for c in body["customers"]}
    assert counts[two_orders] == 2
    assert counts[no_orders] == 0
    assert counts == {
        c["customer_id"]: expected.get(c["customer_id"], 0) for c in _csv("customers")
    }


def test_defaults_apply_without_params(client):
    body = client.get("/customers").json()
    assert body["page"] == 1
    assert len(body["customers"]) > 0


def test_invalid_pagination_is_rejected(client):
    for params in ({"page": 0}, {"page": -1}, {"pageSize": 0}, {"pageSize": 101}, {"page": "x"}):
        assert client.get("/customers", params=params).status_code == 422


def test_cors_allows_frontend_origin(client):
    r = client.get("/customers", headers={"Origin": "http://localhost:5173"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
