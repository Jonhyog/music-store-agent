# 10: Filing a Complaint through the chat

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** An identified Customer tells the Assistant about a problem. The Assistant summarizes it (category, related Order, description), asks for confirmation, files the Complaint, and replies with a protocol number and the 24-business-hour response promise. Visitors are told they need to be identified and are given the WhatsApp number and email. Complaints survive restarts and re-seeding.

**Blocked by:** 07 (Customer Orders).

**Status:** ready-for-agent

- [ ] A `complaints` table: `complaint_id`, `customer_id` (required), `order_id` (optional), `category` (`product_defect | delivery | service | payment | other`), `description`, `conversation_id`, `created_at` (real wall-clock time). There is no status.
- [ ] Re-seeding rebuilds catalog, customer and order tables and keeps Complaints. A reset option wipes everything.
- [ ] Tool: register a Complaint (category, description, optional Order id), with the Customer from runtime context and the Conversation id recorded. It refuses Visitors and Orders that don't belong to the Customer, and returns the Complaint id and creation time.
- [ ] The prompt adds: summarize and ask for confirmation before filing, file only after the customer confirms, reply with "Protocolo #N" and the 24-business-hour promise, send Visitors to the WhatsApp number and email (retrieved from the Policy Manual, not hard-coded), and route anything else it can't settle to those channels.
- [ ] Tests at the HTTP seam with the fake chat model: filing a Complaint persists it with the right fields, filing against another Customer's Order is refused, a Visitor is refused.
- [ ] Tests at the seed seam: re-seeding keeps existing Complaints, and reset removes them.
- [ ] A Bruno request for a complaint conversation.
