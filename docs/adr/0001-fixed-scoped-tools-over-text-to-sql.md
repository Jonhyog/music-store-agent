# Fixed, customer-scoped tools instead of text-to-SQL

The Assistant reaches the store database only through a small set of fixed, parameterized tools (search/get Products, list active Promotions, list/get the Customer's own Orders, list Categories), never through model-written SQL. Orders must be visible only to the Customer they belong to, and with no authentication the only reliable place to enforce that is code: the order tools take no customer argument and read the Customer from the request context, so no prompt can widen their reach. Text-to-SQL would make that scoping depend on the model's obedience, and small local models (our default) write unreliable SQL.

## Considered Options

- **Text-to-SQL agent**: more flexible for ad-hoc questions, but scoping becomes a prompt concern and query quality depends on model size.
- **Fixed tools** (chosen): less flexible; adding a new kind of question means adding a tool.

## Consequences

- Derived money values (Promotional Price, PIX price) are computed in the tools, not by the model.
- Asking for another Customer's Order is indistinguishable from asking for a non-existent one ("not found").
