# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Authenticated blog system combining Quartz 4 (static site generator) with a Flask backend. Users authenticate via magic link emails (Mailgun), then access Quartz-generated static content served through Flask's protected file serving.

## Architecture

**Request flow:** Browser → Flask (port 5000) → auth check → serve static files from `public/`

**Two-stage build:** Markdown in `content/` → Quartz builds HTML to `public/` → Flask serves `public/` behind auth

**Key layers:**
- `content/` — Markdown source files, synced from separate repo (`git@github.com:jonnyallred/writings.git`). Only files with `publish: true` frontmatter are included in builds (via `ExplicitPublish` plugin). Gitignored; cloned/pulled automatically by `scripts/build.sh`
- `quartz/` — Quartz 4 framework (TypeScript/TSX, Preact components, remark/rehype plugins). Custom components: `TopNav.tsx`, `MetadataSidebar.tsx`, `EmailFeedback.tsx`
- `quartz.config.ts` / `quartz.layout.ts` — Site configuration and page layout
- `backend/` — Flask app with magic link auth, SQLite sessions, Mailgun email, rate limiting
- `scripts/` — Build and deployment bash scripts, systemd service file
- `public/` — Generated static site (build output, gitignored)

**Backend modules:**
- `app.py` — Flask app with `before_request` auth middleware
- `auth.py` — Blueprint: login, request-link (rate limited 5/hr), verify token, logout
- `models.py` — SQLite schema: `magic_links` and `sessions` tables
- `static_auth.py` — Protected file serving with directory traversal prevention
- `email_service.py` — Mailgun API integration
- `discovery.py` — Orphaned page detection (`GET /api/orphans`)

## Common Commands

```bash
# Build static site
npx quartz build

# Build and serve locally (Quartz dev server)
npx quartz build --serve

# Run Flask backend
python3 backend/app.py

# TypeScript + Prettier check
npm run check

# Auto-format code
npm run format

# Run tests
npm run test

# Install dependencies
npm install
pip install -r backend/requirements.txt

# Initialize database
python3 backend/models.py

# Database cleanup (expired tokens/sessions)
python3 backend/cleanup.py

# Deploy
./scripts/deploy_dev.sh
./scripts/deploy_prod.sh
```

## Configuration

- `.env` — Secret keys, Mailgun credentials, session settings (never commit)
- `.node-version` — Node 22.16.0
- `.prettierrc` — 100 char width, no semicolons, trailing commas, 2-space tabs
- `tsconfig.json` — Strict mode, Preact JSX
