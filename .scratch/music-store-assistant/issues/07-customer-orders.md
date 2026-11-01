# 07: Customer Orders

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** An identified Customer asks about their Orders and gets their status, items, tracking code, estimated delivery and any cancellation note. They can ask whether a return is possible, and get an answer based on the store's reference date. They are greeted by first name. Nobody can see another Customer's Orders, and Visitors are told the Assistant needs to know who they are (ADR 0001).

**Blocked by:** 04 (Chat API: streaming Assistant that answers catalog questions).

**Status:** ready-for-agent

- [ ] Tool: list my Orders, optionally by Order Status. Tool: get my Order by id. Both read the Customer only from runtime context and take no customer argument.
- [ ] Order results include Order Status, total, payment method, tracking code, estimated delivery, notes, and Order Items with Product names and quantities.
- [ ] For a Visitor, the tools return a uniform "customer not identified" result. For an Order that doesn't exist or belongs to someone else, they return an identical "not found" result.
- [ ] The prompt injects the reference date and the Customer's first name. The Assistant greets the Customer by first name, treats the estimated delivery date as the delivery date for delivered Orders and says so, and tells Visitors it needs them identified to answer about Orders.
- [ ] Tests cover listing my Orders, filtering by status, getting my Order, another Customer's Order matching a non-existent Order exactly, and Visitor refusal for both tools.
- [ ] Bruno requests for an Order question as a Customer and as a Visitor.
