import os
import logging
from datetime import timedelta
from flask import Flask, session, request, redirect, url_for, jsonify
from config import Config
from auth import bp as auth_bp
import static_auth
from discovery import find_orphaned_pages, get_page_metadata

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, template_folder='templates')

# Load configuration
app.config.from_object(Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=Config.SESSION_TIMEOUT_DAYS)

# Register authentication blueprint
app.register_blueprint(auth_bp)


@app.before_request
def check_authentication():
    """
    Run before every request.

    - Allow auth routes without authentication
    - Check session validity for other routes
    - Update session last_accessed timestamp
    """
    # Allow auth routes without authentication
    if request.path.startswith('/auth/'):
        return None

    # Check if user is authenticated
    if not static_auth.is_authenticated():
        logger.info(f"Unauthenticated access to {request.path}, redirecting to login")
        return redirect(url_for('auth.login'))

    # Update session last_accessed timestamp
    session_id = session.get('session_id')
    if session_id:
        try:
            from models import Session as SessionModel
            SessionModel.update_last_accessed(session_id)
        except Exception as e:
            logger.error(f"Error updating session: {e}")

    return None


# Catch-all route for serving static files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from public/ with authentication"""
    return static_auth.serve_protected_static(path)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by returning index.html (for SPA routing)"""
    return static_auth.serve_protected_static('index.html')


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return "Internal server error", 500


@app.route('/api/orphans', methods=['GET'])
def get_orphans():
    """
    Get list of orphaned pages (pages with no backlinks)

    Returns:
        JSON response with list of orphaned pages and metadata
    """
    try:
        # Check authentication
        if not static_auth.is_authenticated():
            return jsonify({'error': 'Unauthorized'}), 401

        # Find orphaned pages
        orphans = find_orphaned_pages()

        # Get metadata for all pages
        metadata = get_page_metadata()

        # Build response with metadata
        orphan_details = []
        for orphan_path in orphans:
            if orphan_path in metadata:
                orphan_details.append({
                    'path': orphan_path,
                    'title': metadata[orphan_path]['title'],
                    'tags': metadata[orphan_path]['tags'],
                    'date': metadata[orphan_path]['date'],
                })
            else:
                orphan_details.append({
                    'path': orphan_path,
                    'title': orphan_path,
                    'tags': [],
                    'date': None,
                })

        return jsonify({
            'orphans': orphan_details,
            'count': len(orphan_details),
        })

    except Exception as e:
        logger.error(f"Error retrieving orphaned pages: {e}")
        return jsonify({'error': 'Failed to retrieve orphaned pages'}), 500


if __name__ == '__main__':
    # Make sure database is initialized
    from models import Database
    db = Database()
    logger.info(f"Database initialized at {Config.DATABASE_PATH}")

    # Run Flask app
    logger.info("Starting Flask app...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
