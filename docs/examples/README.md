# Example conversations

Real transcripts saved by the eval script (`backend/evals`) against the default local model, `qwen3:4b`, with the reference date `2026-03-25`. Tool calls and their results are shown inline.

| File | Shows |
|---|---|
| [01-return-delivered-order.md](01-return-delivered-order.md) | Live data and policy: a Customer asks to return a delivered Order. The Assistant reads the Order, searches the return rules and compares the dates with today. |
| [02-store-address-policy.md](02-store-address-policy.md) | Policy retrieval: the store address comes from a search, not from memory. |
| [03-complaint-confirmation.md](03-complaint-confirmation.md) | Complaint flow: the Assistant summarizes and asks for confirmation, and files only after "yes". |
| [04-accessory-redirect.md](04-accessory-redirect.md) | Scope: Accessories are not sold, partner stores are suggested. |
| [05-jailbreak-prompt-leak.md](05-jailbreak-prompt-leak.md) | Safety: a request to reveal the instructions is declined. |

## Known limitations seen in the eval

- `qwen3:4b` is the only model evaluated here. `qwen3:8b` was not pulled and no valid OpenAI key was configured, so those runs could not happen. Run `uv run python -m evals` on a machine that has them.
- The small model is not deterministic. Across runs, it sometimes skipped `search_policies` on a return question (answering from the Order alone), called `search_policies` for an off-topic question, or ignored a tool and answered from memory. The prompt pass fixed most of these, but they are not guaranteed.
- Guardrails are prompt-only. If the eval keeps showing drift off scope, the next step is an input classifier that screens each message before it reaches the Assistant (the "more time" item).
- The eval's complaint scenario really files a Complaint in the database it runs against.
