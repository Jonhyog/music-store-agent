# 01: Backend skeleton: seed the store and list Customers

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** A developer can set up the backend with one install command and one seed command, start the API, and list Customers with how many Orders each has. This establishes the backend project (Python 3.12, uv, FastAPI, pydantic-settings with a committed example env file), the SQLite store built from the read-only `data/` CSVs, and the HTTP test harness (Seam A) that every later backend ticket reuses.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] One seed command builds the store database from `data/` following the README schema (categories, products, promotions, customers, orders, order_items), parses Product specs from JSON, and leaves the source files untouched.
- [ ] The generated database is gitignored. Settings (database path, CORS origins, reference date default `2026-03-25`) load from environment / `.env`, with an example file committed.
- [ ] `GET /customers?page&pageSize` returns `{ customers, page, total }`. Each Customer has `customer_id`, `name`, `phone`, `email`, `city` and `order_count`, and pagination parameters are validated.
- [ ] CORS is configured for the frontend dev origin.
- [ ] A pytest harness runs the real app over HTTP against a temporary database seeded from `data/`. There are tests for `/customers` pagination, totals and `order_count`, e.g. a Customer with two Orders reports 2 and a Customer with none reports 0.
- [ ] A Bruno collection exists with a `/customers` request.
