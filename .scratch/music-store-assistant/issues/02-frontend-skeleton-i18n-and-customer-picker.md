# 02: Frontend skeleton: app shell, i18n and Customer picker

Parent spec: `.scratch/music-store-assistant/spec.md`

**What to build:** A person opens the web app, sees the store's header in Portuguese (switchable to English), navigates between Chat and Complaints, lands on a not-found page for unknown routes, and picks who they are from a searchable Customer list (Visitor first) loaded from the API.

**Blocked by:** 01 (Backend skeleton: seed the store and list Customers).

**Status:** ready-for-agent

- [ ] A Vite + React + TypeScript SPA scaffolded with the shadcn CLI, managed with pnpm, with type-checking and lint scripts.
- [ ] Routes: Chat at the root (placeholder body), Complaints (placeholder body), and a not-found page for anything else.
- [ ] `react-i18next` with `pt-BR` (default) and `en`. A header toggle switches language and the choice persists in local storage. No hard-coded UI strings outside the translation files.
- [ ] The header shows the store name, navigation links to Chat and Complaints, and the language toggle.
- [ ] On the Chat route, the header shows a searchable Customer Combobox listing "Name · City · N pedidos", with Visitor first and selected by default, loaded once from `/customers` with `pageSize=50`.
- [ ] The selected identity (Customer or Visitor) is held in app state, ready for the chat to send as `x-customer-id` (no header for Visitor).
- [ ] The backend URL comes from frontend configuration.
