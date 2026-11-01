# 06: Prices and Promotions

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** A person asking about a Product's price gets exact figures: the List Price, the Promotional Price with its discount percentage when a Promotion is active, and the PIX price only when no Promotion applies. They can list active Promotions, optionally by Category. Out-of-stock, discontinued, coming-soon and expired-promotion questions are handled as the Policy Manual prescribes.

**Blocked by:** 04 (Chat API: streaming Assistant that answers catalog questions).

**Status:** ready-for-agent

- [ ] Product results from the catalog tools include `list_price`, the active Promotion (campaign name and discount %) if any, `promotional_price`, and `pix_price`, all computed in code. The PIX Discount (5%) applies only when there is no active Promotion.
- [ ] Only Promotions with `is_active = 1` count. When several active Promotions target one Product, the highest discount wins.
- [ ] A tool lists active Promotions, optionally filtered by Category, with the computed prices.
- [ ] The prompt adds presentation rules: Promotional Price always shown next to List Price and discount % (§6.2). Out of stock means saying it's unavailable and suggesting available alternatives. Discontinued means saying it's no longer sold and offering equivalents. Coming soon means saying it isn't available yet. An expired Promotion is stated honestly, with the current price (§7.3).
- [ ] Tests, reading tool-output events, cover a Product with an active Promotion (correct Promotional Price, no PIX price), a Product without one (correct PIX price), a Product whose only Promotions are inactive, and the active-Promotions listing with and without a Category filter.
