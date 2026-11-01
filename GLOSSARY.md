# Empório da Música — Customer Service

Language for the virtual customer-service assistant of Empório da Música, a musical-instrument store in Campo Grande/MS that answers customers about the catalog, their orders, and store policies.

## Catalog

**Product**:
A musical instrument the store sells, identified by its name, with a list price in BRL, a stock quantity, and a catalog status.
_Avoid_: Item, SKU, article

**Category**:
A family of instruments that groups Products (e.g. Violões, Guitarras, Ukuleles).
_Avoid_: Department, type

**Catalog Status**:
Whether a Product can be sold now (`active`), will be sold later (`coming_soon`), or is no longer sold (`discontinued`).

**Accessory**:
A non-instrument good (strings, picks, cables, cases, pedals, amplifiers) that the store does not sell.

## Pricing

**List Price**:
The Product's regular price before any discount.
_Avoid_: Table price, base price, original price

**Promotion**:
A percentage discount campaign attached to one Product; only an active Promotion affects what the customer pays.
_Avoid_: Sale, deal, offer

**Promotional Price**:
The List Price minus the discount of the Product's active Promotion.

**PIX Discount**:
The 5% discount for paying with PIX, which never stacks on a Promotional Price.

## Orders

**Customer**:
A person registered with the store who can place Orders and can only see their own Orders.
_Avoid_: User, client, account, buyer

**Visitor**:
Someone chatting with the assistant who has not been identified as a Customer; a Visitor can ask about Products, Promotions and policies but has no Orders to see.
_Avoid_: Guest, anonymous user

**Order**:
A purchase placed by one Customer, with a status, a payment method, a stored total, and optionally a tracking code and estimated delivery date.
_Avoid_: Purchase, sale, transaction

**Order Item**:
One Product and its quantity within an Order.
_Avoid_: Line item, order line

**Order Status**:
Where an Order is in its lifecycle: `pending`, `confirmed`, `shipped`, `delivered`, or `cancelled`.

## Assistance

**Assistant**:
The store's virtual customer-service agent that answers Customers and Visitors in the store's voice.
_Avoid_: Bot, chatbot, AI

**Conversation**:
One continuous exchange between the Assistant and a single Customer or Visitor; it never changes hands to someone else.
_Avoid_: Session, chat, thread

**Complaint**:
A grievance a Customer raises through the Assistant, recorded for the store team to follow up on.
_Avoid_: Ticket, issue, claim

## Policies

**Policy Manual**:
The store's internal manual of customer-service policies and procedures (hours, payment, returns, shipping, promotions, warranty, privacy).
_Avoid_: FAQ, terms
