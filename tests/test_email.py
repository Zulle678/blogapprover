from src.services.email_service import get_email_handler
from src.config.settings import EMAIL_RECIPIENT
import logging

logging.basicConfig(level=logging.INFO)

def test_email_functionality():
    handler = get_email_handler()
    
    # Test markdown email
    markdown_content = """
    # Test Blog Post
    
    This is a **test** email with markdown formatting.
    
    ## Features:
    * Markdown support
    * HTML conversion
    * Exchange integration
    
    > This is a blockquote
    """
    
    # Send test email
    handler.send_markdown_email(
        subject="Test Markdown Email",
        markdown_content=markdown_content,
        to_recipients=[EMAIL_RECIPIENT]
    )
    
    # Check inbox
    processed_emails = handler.check_inbox(hours_back=1)
    print(f"Found {len(processed_emails)} unread emails in the last hour")

if __name__ == "__main__":
    test_email_functionality()