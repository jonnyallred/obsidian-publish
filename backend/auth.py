from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from email_service import send_magic_link, is_valid_email
from models import MagicLink, Session, Database
from config import Config
import logging

# Create blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter (will be initialized by app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


@bp.route('/login', methods=['GET'])
def login():
    """Display login form"""
    return render_template('login.html')


@bp.route('/request-link', methods=['POST'])
@limiter.limit("5 per hour")
def request_magic_link():
    """Generate and send a magic link"""
    email = request.form.get('email', '').strip().lower()

    # Validate email
    if not email or not is_valid_email(email):
        return render_template('error.html', message="Please enter a valid email address"), 400

    try:
        # Generate magic link token
        token = MagicLink.create(
            email,
            expiration_minutes=Config.TOKEN_EXPIRATION_MINUTES
        )

        # Build magic link URL
        magic_link_url = f"{Config.BASE_URL}/auth/verify/{token}"

        # Send email
        success = send_magic_link(email, magic_link_url)

        if success:
            logger.info(f"Magic link sent to {email}")
            return render_template('check_email.html', email=email)
        else:
            logger.error(f"Failed to send magic link to {email}")
            return render_template(
                'error.html',
                message="Failed to send email. Please try again later."
            ), 500

    except Exception as e:
        logger.error(f"Error processing magic link request: {e}")
        return render_template(
            'error.html',
            message="An error occurred. Please try again."
        ), 500


@bp.route('/verify/<token>', methods=['GET'])
def verify_magic_link(token: str):
    """Verify magic link and create session"""
    try:
        # Verify token
        is_valid, email = MagicLink.verify(token)

        if not is_valid:
            return render_template(
                'error.html',
                message="This link is invalid or has expired. Please request a new one."
            ), 400

        # Mark token as used
        MagicLink.mark_used(token)

        # Create session
        session_id = Session.create(email)

        # Set session cookie
        session['session_id'] = session_id
        session['email'] = email
        session.permanent = True

        logger.info(f"User {email} logged in via magic link")

        # Redirect to home
        return redirect('/')

    except Exception as e:
        logger.error(f"Error verifying magic link: {e}")
        return render_template(
            'error.html',
            message="An error occurred. Please try again."
        ), 500


@bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout user and clear session"""
    try:
        session_id = session.get('session_id')
        email = session.get('email')

        if session_id:
            Session.delete(session_id)
            logger.info(f"User {email} logged out")

        # Clear session
        session.clear()

        return redirect(url_for('auth.login'))

    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return redirect(url_for('auth.login'))
