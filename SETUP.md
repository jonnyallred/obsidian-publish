# Authenticated Quartz Blog - Setup Guide

This project is a complete authenticated blog system built with Quartz 4, Flask, and SQLite.

## Quick Start

### Prerequisites
- Node.js (v18+)
- Python 3.8+
- Git

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   pip install -r backend/requirements.txt
   ```

2. **Configure environment:**
   Edit `.env` with your settings:
   ```bash
   SECRET_KEY=<generate new with: python3 -c "import secrets; print(secrets.token_hex(32))">
   MAILGUN_API_KEY=<your mailgun key>
   MAILGUN_DOMAIN=mg.yourdomain.com
   FROM_EMAIL=noreply@yourdomain.com
   BASE_URL=https://yourdomain.com
   ```

3. **Initialize database:**
   ```bash
   python3 backend/models.py
   ```

4. **Build Quartz:**
   ```bash
   npx quartz build
   ```

5. **Start Flask app:**
   ```bash
   python3 backend/app.py
   ```

Visit `http://localhost:5000` in your browser.

## Architecture

### Frontend (Quartz)
- **`quartz.config.ts`** - Configuration with ExplicitPublish filter
- **`quartz.layout.ts`** - Layout with custom components
- **`quartz/components/`** - Custom React components:
  - `TopNav.tsx` - Top navigation bar
  - `MetadataSidebar.tsx` - Date, tags, reading time
  - `EmailFeedback.tsx` - Email feedback links
- **`content/`** - Markdown content with `publish: true/false` frontmatter

### Backend (Flask)
- **`backend/app.py`** - Main Flask application with middleware
- **`backend/auth.py`** - Magic link authentication blueprint
- **`backend/models.py`** - Database schema and models
- **`backend/email_service.py`** - Mailgun integration
- **`backend/static_auth.py`** - Protected static file serving
- **`backend/discovery.py`** - Orphaned pages detection
- **`backend/config.py`** - Configuration loader
- **`backend/database.db`** - SQLite database
- **`backend/templates/`** - HTML templates (login, check_email, error)

## Authentication Flow

1. User visits site → redirected to `/auth/login`
2. User enters email → POST to `/auth/request-link`
3. Flask generates token and sends via Mailgun
4. User clicks link → GET `/auth/verify/<token>`
5. Token validated, session created, user authenticated
6. User can now access all static files from `public/`

## Content Management

### Publish/Draft System

Add frontmatter to control visibility:
```yaml
---
title: My Post
date: 2026-01-25
publish: true     # Set to false to hide from site
tags:
  - blog
  - tutorial
---
```

Only pages with `publish: true` appear in the built site.

### Building Content

```bash
# Build static site (only published content)
npx quartz build

# View in browser (requires authentication)
# http://localhost:5000
```

## API Endpoints

### Public Endpoints
- `GET /auth/login` - Login form
- `POST /auth/request-link` - Request magic link (rate limited: 5/hour)
- `GET /auth/verify/<token>` - Verify magic link and create session
- `POST /auth/logout` - Logout user

### Protected Endpoints
- `GET /` - Home page (all static files)
- `GET /api/orphans` - List pages with no backlinks (requires auth)

## Deployment

### Development Deployment
```bash
./scripts/deploy_dev.sh
```

This script:
- Pulls latest from Git
- Installs dependencies
- Builds Quartz
- Restarts Flask app

### Production Deployment

1. Configure `PROD_SERVER`, `PROD_USER`, `PROD_PATH` in `scripts/deploy_prod.sh`
2. Run:
   ```bash
   ./scripts/deploy_prod.sh
   ```

### Systemd Service Setup (Production)

1. Copy service file:
   ```bash
   sudo cp scripts/blog.service /etc/systemd/system/
   ```

2. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable blog
   sudo systemctl start blog
   ```

3. Check status:
   ```bash
   sudo systemctl status blog
   journalctl -u blog -f
   ```

## Security

### Implemented Features
- Magic link authentication (no passwords)
- Session-based authorization
- Rate limiting (5 requests/hour on login endpoint)
- Secure session cookies (httponly, samesite)
- Directory traversal protection
- CSRF protection via Flask session
- Database cleanup (expired tokens, old sessions)

### Additional Hardening (Production)
- Set `SESSION_COOKIE_SECURE=True` in `.env` (requires HTTPS)
- Use strong `SECRET_KEY` (32+ bytes random)
- Enable HTTPS with SSL certificate (Let's Encrypt)
- Configure Mailgun with SPF/DKIM
- Regular backups of `backend/database.db`

## Database Cleanup

Run daily to clean up expired data:
```bash
python3 backend/cleanup.py
```

Add to crontab:
```bash
0 3 * * * /usr/bin/python3 /path/to/backend/cleanup.py
```

## Testing

### Manual Testing Checklist

- [ ] Login flow works end-to-end
- [ ] Expired tokens are rejected
- [ ] Used tokens cannot be reused
- [ ] Session persists across page loads
- [ ] Unauthenticated access redirected to login
- [ ] All static files (CSS, JS, fonts) load correctly
- [ ] Logout clears session
- [ ] `/api/orphans` returns correct list
- [ ] Rate limiting prevents brute force
- [ ] Metadata sidebar shows date, tags, reading time
- [ ] TopNav navigation works
- [ ] Email feedback links have correct subject

### Testing Magic Link Flow
1. Visit `http://localhost:5000`
2. Enter email address
3. Check email inbox/spam for link
4. Click link
5. Should redirect to homepage (authenticated)
6. Open `/api/orphans` to verify API works

## Troubleshooting

### Email not sending
- Check `.env` has correct Mailgun credentials
- Verify Mailgun domain is configured
- Check Flask app logs: `tail -f backend/app.log`

### Database errors
- Delete `backend/database.db` to reset
- Run `python3 backend/models.py` to reinitialize

### Rate limiting too strict
- Edit `TOKEN_EXPIRATION_MINUTES` in `.env`
- Change `@limiter.limit("5 per hour")` in `backend/auth.py`

### Files not building
- Check content has `publish: true` frontmatter
- Verify markdown syntax is valid
- Run `npx quartz build --debug`

## License

Quartz is licensed under MIT. See `LICENSE.txt` for details.

## Support

For issues with:
- **Quartz**: https://quartz.jzhao.xyz/
- **Flask**: https://flask.palletsprojects.com/
- **Mailgun**: https://documentation.mailgun.com/
