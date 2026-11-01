# 11: Complaints screen for staff

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** Store staff open the Complaints screen and see every recorded Complaint as cards, newest first. They can filter by Customer, page through results, and refresh manually. No update, resolve or delete actions; that is the documented trade-off.

**Blocked by:** 10 (Filing a Complaint through the chat).

**Status:** ready-for-agent

- [ ] `GET /complaints?page&pageSize&customerId` returns `{ complaints, page, total }`, newest first. Each item has `complaint_id`, `customer_id`, `customer_name`, `order_id | null`, `category`, `description`, `conversation_id` and `created_at`.
- [ ] The endpoint ignores `x-customer-id` (staff view). An unknown `customerId` returns an empty list.
- [ ] Tests cover ordering, pagination, filtering by Customer, an unknown Customer returning empty, and the customer header being ignored.
- [ ] Bruno requests for listing and filtering Complaints.
- [ ] The Complaints route shows a Customer filter Combobox (first option "all Customers"), a grid of cards (protocol number, category badge, Customer name, Order number if any, relative date with exact time on hover, description), pagination, an empty state, and a manual refresh button.
- [ ] The Customer and model pickers are not shown on this route. All strings go through i18n.
