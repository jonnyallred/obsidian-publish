# CLAUDE.md

This file provides guidance for AI assistants working with this codebase.

## Project Overview

This is an authenticated digital garden and notes publishing platform built on **Quartz v4** (static site generator) with a **Flask backend** for authentication and content serving. It transforms Obsidian-style markdown notes into a website with magic link authentication and a publish/draft content system.

## Repository Structure

```
├── quartz/                 # TypeScript frontend (static site generator)
│   ├── cli/                # CLI argument parsing and command handlers
│   ├── components/         # Preact UI components (~32 components)
│   │   ├── pages/          # Page-level components (Content, Folder, Tag, 404)
│   │   ├── scripts/        # Client-side JavaScript
│   │   └── styles/         # SCSS component stylesheets
│   ├── plugins/            # Plugin system
│   │   ├── transformers/   # Markdown → HTML transformations (13 plugins)
│   │   ├── filters/        # Content filtering (ExplicitPublish, Draft)
│   │   └── emitters/       # File output generation (14 plugins)
│   ├── processors/         # Content processing pipeline (parse, filter, emit)
│   ├── util/               # Utility functions (paths, file trie, theme, etc.)
│   ├── styles/             # Global SCSS stylesheets
│   ├── i18n/               # Internationalization (30+ locales)
│   └── static/             # Static assets
├── backend/                # Flask Python web server
│   ├── app.py              # Main Flask application and routes
│   ├── auth.py             # Authentication blueprint (magic links)
│   ├── models.py           # Database models (MagicLink, Session)
│   ├── static_auth.py      # Authenticated static file serving
│   ├── discovery.py        # Orphaned page detection
│   ├── email_service.py    # Mailgun email integration
│   ├── config.py           # Configuration loader
│   ├── cleanup.py          # Database maintenance script
│   └── templates/          # Jinja2 HTML templates
├── content/                # Markdown source files for publishing
├── docs/                   # Quartz documentation
├── scripts/                # Deployment scripts (build, deploy_dev, deploy_prod)
├── quartz.config.ts        # Main Quartz build/plugin configuration
├── quartz.layout.ts        # Page layout and component composition
├── Dockerfile              # Container configuration (Node 22-slim)
└── SETUP.md                # Comprehensive setup guide
```

## Tech Stack

**Frontend (Quartz):**
- TypeScript 5.9+ with strict mode
- Preact (lightweight React alternative) for UI components
- remark/rehype ecosystem for markdown processing
- esbuild for bundling
- SCSS with lightningcss for styling
- D3.js and Pixi.js for graph visualization

**Backend (Flask):**
- Python 3.8+ with Flask 3.0
- SQLite3 for sessions/tokens
- Flask-Login + Mailgun for magic link auth
- Flask-Limiter for rate limiting

## Common Commands

```bash
# Install dependencies
npm ci

# Build the static site
npx quartz build

# Build and serve with hot reload
npx quartz build --serve

# Run TypeScript type checking + Prettier format check
npm run check

# Auto-format code with Prettier
npm run format

# Run tests
npm test

# Backend (from project root)
pip install -r backend/requirements.txt
python backend/app.py
```

## Code Style and Conventions

### TypeScript/Frontend

- **No semicolons** - enforced by Prettier
- **Print width:** 100 characters
- **Trailing commas:** always (including function parameters)
- **Indentation:** 2 spaces
- **Quotes:** double quotes (Prettier default)
- **Strict TypeScript:** `noUnusedLocals`, `noUnusedParameters`, strict null checks
- **JSX:** Preact (`jsxImportSource: "preact"`)
- **Module system:** ESNext (ES modules with `"type": "module"` in package.json)
- **Node version:** >=22 required (enforced by `.npmrc` engine-strict)

### Testing

- Uses Node.js built-in `node:test` module with `tsx` transpiler
- Test files are colocated with source: `*.test.ts` next to implementation
- Uses `describe`/`test` blocks with `node:assert` for assertions
- Run with `npm test`

### Plugin Architecture

All plugins follow this pattern:
```typescript
export const PluginName: QuartzPlugin<Options> = (opts) => ({
  name: "PluginName",
  // Transformer plugins:
  textTransform?: (ctx, src) => transformed,
  markdownPlugins?: (ctx) => remarkPlugins[],
  htmlPlugins?: (ctx) => rehypePlugins[],
  // Filter plugins:
  shouldPublish?: (ctx, content) => boolean,
  // Emitter plugins:
  emit?: async (ctx, content, resources) => outputPaths[],
})
```

Three plugin types:
1. **Transformers** - modify markdown/HTML during parsing (in `quartz/plugins/transformers/`)
2. **Filters** - determine which content gets published (in `quartz/plugins/filters/`)
3. **Emitters** - generate output files (in `quartz/plugins/emitters/`)

Plugins are registered in `quartz.config.ts`.

### Component Pattern

Quartz components are Preact functional components with optional bundled resources:
```typescript
const MyComponent: QuartzComponent = (props: QuartzComponentProps) => {
  return <div>...</div>
}
MyComponent.css = `/* component styles */`
MyComponent.afterDOMLoaded = `// client-side JS`
```

Components are composed in `quartz.layout.ts` for page layout.

### Content Publishing

- Content lives in `content/` as markdown files
- The `ExplicitPublish` filter requires `publish: true` in frontmatter for content to appear
- Frontmatter fields: `title`, `date`, `tags`, `publish`, `description`, `aliases`
- Draft posts use `publish: false` or omit the field entirely

### Backend Conventions

- Flask blueprints for route organization (`auth.py` as auth blueprint)
- Magic link authentication flow (no passwords)
- Rate limiting on auth endpoints (5 requests/hour)
- Session cookies: httponly, samesite
- SQLite database at `backend/database.db` (gitignored)
- Environment config via `.env` file (gitignored)

## Architecture Notes

### Build Pipeline

1. **Glob** - discover all markdown files in content directory
2. **Parse** - convert markdown to AST using remark (parallelized via workerpool)
3. **Transform** - apply transformer plugins (syntax highlighting, links, math, etc.)
4. **Filter** - remove unpublished content via filter plugins
5. **Emit** - generate static HTML, assets, sitemap, RSS via emitter plugins
6. **Serve** - optional dev server with file watching and hot reload

### Key Configuration Files

| File | Purpose |
|------|---------|
| `quartz.config.ts` | Plugin selection, theme, site metadata |
| `quartz.layout.ts` | Page layout and component composition |
| `tsconfig.json` | TypeScript compiler options (strict, ESNext) |
| `.prettierrc` | Code formatting rules |
| `backend/.env` | Backend secrets (SECRET_KEY, MAILGUN_API_KEY, etc.) |

### Important Directories (gitignored)

- `public/` - generated static site output
- `.quartz-cache/` - build cache
- `node_modules/` - npm dependencies
- `backend/database.db` - SQLite database

## Deployment

- **Docker:** Multi-stage build with Node 22-slim, runs `npx quartz build --serve`
- **Manual:** Scripts in `scripts/` for dev and prod deployment
- **Systemd:** `blog.service` for production Linux deployments
- No CI/CD pipeline - deployment is manual via scripts

## Common Tasks

### Adding a new transformer plugin
1. Create file in `quartz/plugins/transformers/`
2. Export the plugin following the `QuartzTransformerPlugin` interface
3. Register in `quartz/plugins/index.ts`
4. Add to `quartz.config.ts` plugins array

### Adding a new component
1. Create `.tsx` file in `quartz/components/`
2. Implement as `QuartzComponent` with typed props
3. Export from `quartz/components/index.ts`
4. Add to layout in `quartz.layout.ts`

### Adding new content
1. Create markdown file in `content/`
2. Add frontmatter with `publish: true` to make it visible
3. Build with `npx quartz build` to generate static output

### Running the full stack locally
1. `npm ci` to install frontend dependencies
2. `npx quartz build` to generate static site into `public/`
3. `pip install -r backend/requirements.txt` for backend deps
4. Copy `backend/.env.example` to `backend/.env` and configure
5. `python backend/app.py` to start the Flask server
