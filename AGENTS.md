# AGENTS.md

Read this file in full before taking any action. Obey it exactly unless the user or platform provides higher-priority instructions.

---

## 0. TLDR For The Agent

On every session start, do this in order:

1. Read this file completely.
2. Check the log file path in §1.
3. Append a `SESSION START` entry using §3.1.
4. For every user turn, append a summary entry using §3.2.

Do not skip logging or rewrite old log entries. Sub-agents and worktrees use the same log file.

---

## 1. Log File — Location And Lifecycle

The log file is named `log.txt` and lives in the same directory as this `AGENTS.md` file — the repository root.

| Platform | Path |
|---|---|
| macOS / Linux | `<directory containing AGENTS.md>/log.txt` |
| Windows | `<directory containing AGENTS.md>\log.txt` |

Resolve the path relative to this file. Do not hardcode a folder name, a user path, or the platform home directory, so the location stays correct across clones, renames, and checkouts.

Rules:

- Create the file if missing.
- Never commit or add the log file to git. Keep `log.txt` in `.gitignore`.
- Append only. Do not rewrite, reorder, or delete prior entries.
- One shared log per checkout. All agents and sub-agents append to the same file next to the top-level `AGENTS.md`, never a private copy.
- Never log secrets. Redact API keys, tokens, cookies, private keys, and sensitive PII.

---

## 2. Session Start

At the beginning of each agent session:

1. Append a short `SESSION START` entry using §3.1.
2. Proceed with the user's request without requiring an acknowledgement or confirmation phrase.

---

## 3. Log Format

### 3.1 Session Start Entry

```text
## [ISO-8601 TIMESTAMP] SESSION START

tool=<exact_harness_or_coding_agent_name>
Repo Root: <absolute_path>
Branch: <git_branch_or_unknown>
Worktree: <worktree_path_or_main>
Parent Agent: <parent_agent_name_or_none>
Language: <js|ts|py|custom:name>
```

### 3.2 Per-Turn Entry

Append after every user message you respond to:

```text
## [ISO-8601 TIMESTAMP] <short title, max 80 chars>

User Prompt (verbatim, secrets redacted):
<exact user message, with secrets replaced by [REDACTED]>

Agent Response Summary:
<2-5 sentences: what was done, why, and any important decision>

Actions:
* <file edited / command run / tool invoked>

Context:
tool=<exact_harness_or_coding_agent_name>
branch=<git_branch_or_unknown>
repo_root=<absolute_path>
worktree=<worktree_path_or_main>
parent_agent=<parent_name_or_none>
```

**Mandatory tool-name rule:** Every `SESSION START` and per-turn log entry must contain one non-empty `tool=` line with the exact name of the coding harness or agent writing the entry. Replace the template value before writing the log. The entry is invalid if `tool=` is missing, blank, still contains a placeholder, uses a generic label such as `AI`, contains only a model name, or names a different harness. Before responding, verify the value against the harness identity provided by the current runtime and re-read the appended entry to confirm it matches. Never guess the tool name. Correct any mismatch before responding to the user.

### 3.3 Sub-Agent And Worktree Rules

- Sub-agents must log their own entries using the same file.
- Set `parent_agent=` to the parent agent's name.
- Worktrees use the same shared log file, not a per-worktree copy.

### 3.4 What Not To Log

- API keys, tokens, session cookies, OAuth codes, or private keys.
- Sensitive PII.
- Full contents of large files or binary blobs. Reference by path instead.

---

## 4. Quick Checklist For The Agent

Before responding to any user message, confirm:

- [ ] I have read this file in this session.
- [ ] I have appended the session-start entry.
- [ ] I will append a §3.2 entry after this turn.
- [ ] I have verified that `tool=` exactly matches the harness or coding agent currently running.
- [ ] I will not log secrets.

---

## Agent skills

### Issue tracker

Issues live as markdown under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `GLOSSARY.md` + `docs/adr/`. See `docs/agents/domain.md`.
