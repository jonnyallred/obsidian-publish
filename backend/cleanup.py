#!/usr/bin/env python3
"""
Database cleanup script

Removes expired magic links and old sessions.
Should be run periodically (e.g., daily via cron).

Usage:
    python3 cleanup.py
"""

import sys
from pathlib import Path
from models import MagicLink, Session
from config import Config

def cleanup_database():
    """Clean up expired and old data from database"""
    try:
        print("Starting database cleanup...")

        # Delete expired magic link tokens
        expired_count = MagicLink.delete_expired()
        print(f"✓ Deleted {expired_count} expired magic link tokens")

        # Delete old sessions (older than 30 days)
        old_sessions_count = Session.delete_old(days=30)
        print(f"✓ Deleted {old_sessions_count} old sessions")

        # Get database size
        db_path = Path(Config.DATABASE_PATH)
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"✓ Database size: {size_mb:.2f} MB")

        print("✓ Database cleanup complete")
        return True

    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        return False


if __name__ == '__main__':
    success = cleanup_database()
    sys.exit(0 if success else 1)
