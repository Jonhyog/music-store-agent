# 13: README and final documentation

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** An evaluator clones the repo, follows the README to run everything locally (and optionally with the API model), and understands every technical decision, assumption and limitation, plus how AI coding assistants were used, as the challenge brief requires.

**Blocked by:** 09 (Conversation robustness), 11 (Complaints screen for staff), 12 (Prompt hardening and the eval script).

**Status:** ready-for-agent

- [ ] Setup instructions:
  - Install Ollama and pull `qwen3:4b`, `qwen3:8b` and `bge-m3`.
  - Optionally set the OpenAI key.
  - Backend install, seed (and reset), and run.
  - Frontend install and run.
  - Using the Bruno collection.
  - Running tests and the eval.
  - Optional LangSmith.
- [ ] Technical decisions with rationale (framework and approach, models and provider, retrieval architecture, prompt strategy, interface, history persistence, data treatment), linking ADRs 0001–0003. Mention full-manual context as the considered alternative to retrieval.
- [ ] Assumptions: the reference date (default `2026-03-25`), the estimated delivery date standing in for actual delivery, and the Complaints screen as a staff view.
- [ ] Known data problems: product name and description brand mismatches, Policy Manual contradictions, the duplicate email, and most Customers having no Orders.
- [ ] Known limitations:
  - No authentication (the customer header is trusted).
  - In-memory Conversations.
  - Read-only Complaints.
  - No out-of-hours behaviour.
  - Prompt-only guardrails.
  - Any eval findings.
- [ ] What we'd do with more time:
  - Staff authentication.
  - Complaint lifecycle.
  - Per-Customer model entitlements.
  - An input classifier.
  - Persistent Conversations.
- [ ] How AI coding assistants were used, including the design session, glossary, ADRs, spec and tickets workflow.
- [ ] Links to the example conversations. The existing schema documentation is kept.
