import requests
from config import Config


def send_magic_link(email: str, magic_link_url: str, blog_title: str = "My Blog") -> bool:
    """
    Send a magic link via Mailgun

    Args:
        email: Recipient email address
        magic_link_url: Full URL to the magic link (e.g., https://yourdomain.com/auth/verify/token)
        blog_title: Name of the blog

    Returns:
        True if email was sent successfully, False otherwise
    """
    if not Config.MAILGUN_API_KEY or not Config.MAILGUN_DOMAIN:
        print("Warning: Mailgun not configured. Email not sent.")
        return False

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Welcome to {blog_title}</h2>
            <p>Click the link below to log in:</p>
            <p>
                <a href="{magic_link_url}"
                   style="background-color: #007bff; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Log In
                </a>
            </p>
            <p style="color: #666; font-size: 12px;">
                Or paste this link in your browser: <br/>
                {magic_link_url}
            </p>
            <p style="color: #999; font-size: 12px;">
                This link expires in 15 minutes. If you didn't request this link, you can safely ignore this email.
            </p>
        </body>
    </html>
    """

    text_content = f"""
Welcome to {blog_title}

Click the link below to log in:
{magic_link_url}

This link expires in 15 minutes.
If you didn't request this link, you can safely ignore this email.
    """

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{Config.MAILGUN_DOMAIN}/messages",
            auth=("api", Config.MAILGUN_API_KEY),
            data={
                "from": f"{blog_title} <{Config.FROM_EMAIL}>",
                "to": email,
                "subject": f"Your login link for {blog_title}",
                "text": text_content,
                "html": html_content,
            },
            timeout=10
        )

        return response.status_code == 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    # Simple check for basic email format
    return "@" in email and "." in email.split("@")[1] if len(email.split("@")) == 2 else False
