from services.file_service import watch_directory
from services.email_service import get_email_handler
from services.llama_service import get_llama_service
import logging

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting Blog Approver")
        watch_directory()
    except KeyboardInterrupt:
        logger.info("Shutting down Blog Approver")
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        raise

def send_test_email():
    """Send a test email to verify the configuration"""
    try:
        handler = get_email_handler()
        handler.send_email(
            subject="Test Email",
            body="This is a test email from Blog Approver",
            to_recipients=[EMAIL_RECIPIENT]
        )
        logger.info("Test email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")

if __name__ == "__main__":
    main()
    send_test_email()