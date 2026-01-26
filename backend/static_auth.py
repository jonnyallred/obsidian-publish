from flask import session, redirect, url_for, send_from_directory, current_app
from models import Session
import os
import logging

logger = logging.getLogger(__name__)


def is_authenticated() -> bool:
    """
    Check if user has a valid session

    Returns:
        True if authenticated with valid session, False otherwise
    """
    session_id = session.get('session_id')

    if not session_id:
        return False

    # Validate session in database
    return Session.validate(session_id)


def serve_protected_static(path: str):
    """
    Serve static files from public/ directory

    Only authenticated users can access files.
    Unauthenticated users are redirected to login.

    Args:
        path: The requested file path (relative to public/)

    Returns:
        Flask response with the file, or redirect to login
    """
    # Check authentication
    if not is_authenticated():
        logger.info(f"Unauthenticated access attempt to {path}, redirecting to login")
        return redirect(url_for('auth.login'))

    # Update session last_accessed time
    session_id = session.get('session_id')
    if session_id:
        Session.update_last_accessed(session_id)

    # Build the full path to the public directory
    public_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
    public_dir = os.path.abspath(public_dir)

    # Security: prevent directory traversal
    requested_file = os.path.join(public_dir, path)
    requested_file = os.path.abspath(requested_file)

    if not requested_file.startswith(public_dir):
        logger.warning(f"Directory traversal attempt: {path}")
        return "Access denied", 403

    # If path is a directory, serve index.html
    if os.path.isdir(requested_file):
        requested_file = os.path.join(requested_file, 'index.html')
        path = os.path.join(path, 'index.html')

    # Check if file exists
    if not os.path.isfile(requested_file):
        logger.info(f"File not found: {path}")
        return send_from_directory(public_dir, 'index.html')

    # Serve the file
    return send_from_directory(public_dir, path)
