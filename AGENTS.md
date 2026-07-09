# MIRU Backend API — Agent Rules

## Token Savers (WAJIB)

1. **graphify** — `graphify query "<question>"` sebelum Read/Grep/Glob. Graph di `graphify-out/`. Wiki: `graphify-out/wiki/index.md`. Update: `graphify update .`
2. **RTK** — shell commands di-rewrite otomatis via hook (60-90% hemat token). Lihat `RTK.md`.
3. **Ponytail** — solusi paling sederhana yang benar. Lihat `.cursor/rules/imported/ponytail/ponytail.mdc`.
4. **AI Steering lazy** — jangan baca semua `.ai-steering/` upfront. Lihat `.cursor/rules/ai-steering-lazy.mdc`.
5. **Context7** — fetch docs library via MCP, bukan dari memori.

## Graphify Knowledge Graph

This project has its **own** graphify knowledge graph at `graphify-out/` (scoped to this backend repo — not the monorepo root). Run `graphify` commands from `miru-backend/`.

**MANDATORY: Before using Read, Grep, Glob, or Bash to explore the codebase, you MUST run graphify first:**

- `graphify query "<question>"` — scoped subgraph for any codebase or architecture question
- `graphify path "<A>" "<B>"` — dependency path between two symbols
- `graphify explain "<concept>"` — all nodes related to a concept

Only use Read/Grep/Glob directly when graphify has oriented you or `graphify-out/graph.json` does not exist yet.

## Stack

- Django 5.2 + DRF + JWT + PostgreSQL/SQLite
- API docs (OpenAPI): `/api/docs/` · Panduan alur: `/api/guide/`
- Steering docs: `.ai-steering/` (on-demand only)
