# 12: Prompt hardening and the eval script

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** An evaluator runs one script against the running server and each available real model. It plays the challenge scenarios and the safety prompts and saves the transcripts, showing which tools the Assistant chose, that it stays on scope, and that it resists jailbreaks. The system prompt gets its final pass based on what the eval reveals, and 3–5 transcripts become the repo's example conversations.

**Blocked by:** 06 (Prices and Promotions), 07 (Customer Orders), 08 (Policy retrieval), 10 (Filing a Complaint through the chat).

**Status:** ready-for-agent

- [x] An opt-in eval script, outside pytest, drives the running server over HTTP for each available model (or one, with `--model`) and saves transcripts that include tool calls.
- [x] Scenarios:
  - Violões up to R$1000 (catalog).
  - Store address (policy).
  - Takamine GD20 price (pricing).
  - "Can I return my Order?" as a Customer with a delivered Order (Order + policy + reference date).
  - An Accessory request (redirect).
  - Off-topic requests.
  - Jailbreak and role-play attempts.
  - Asking for another Customer's Order.
  - The Complaint flow, checking confirmation before filing.
  - A Visitor trying to complain.
- [x] Checks are behavioural (expected tool called or not called, refusal present, confirmation before filing), not exact wording. The script reports pass/fail per scenario and model.
- [x] The system prompt gets a final pass on scope, Accessories with partner-store suggestion, off-topic decline, jailbreak resistance, never discussing other Customers, and the full section order from the spec.
- [x] 3–5 example conversations are saved in the repo, covering varied scenarios, with at least one consulting live data or applying a policy rule.
- [x] If the eval shows the default local model drifting off scope, record it as a known limitation, with an input classifier as the "more time" item.
